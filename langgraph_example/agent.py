import asyncio
import operator
import os
from typing import Annotated, TypedDict, List, Any, Dict, AsyncGenerator
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END

# .env 파일을 통해 환경 변수(OpenAI API Key 등)를 로드합니다.
load_dotenv()

class AgentState(TypedDict):
    """
    에이전트의 단기 기억(State)을 정의합니다.
    'messages' 리스트는 Annotated와 operator.add를 통해
    각 노드에서 생성된 메시지가 덮어씌워지지 않고 계속 누적되도록 합니다.
    이것이 에이전트가 대화의 문맥을 잃지 않는 핵심 장치입니다.
    """
    messages: Annotated[List[BaseMessage], operator.add]

class LangGraphAgentEngine:
    """
    LangGraph의 핵심 오케스트레이션 로직을 담당하는 범용 엔진 클래스입니다.
    이 엔진은 '판단(LLM)'과 '실행(Tools)'을 반복하는 순환 구조(Cycle)를 구축합니다.
    어떤 특화 에이전트든 이 엔진 위에 도구와 프롬프트만 주입하여 생성할 수 있습니다.
    """
    def __init__(self, model_name: str = "gpt-4o", tools: List[Any] = None, system_prompt: str = ""):
        """
        엔진 초기화 시 사용할 모델, 도구 목록, 그리고 에이전트의 페르소나(System Prompt)를 설정합니다.
        """
        # 모델이 도구를 인식하고 사용할 수 있도록 바인딩합니다.
        self.llm = ChatOpenAI(model=model_name, temperature=0).bind_tools(tools or [])
        # 도구 실행 시 이름으로 빠르게 조회하기 위해 딕셔너리로 관리합니다.
        self.tools_dict = {t.name: t for t in (tools or [])}
        self.system_prompt = system_prompt
        # 최종적으로 컴파일된 그래프 애플리케이션입니다.
        self.app = self._build_graph()

    def _build_graph(self):
        """
        StateGraph를 생성하고 노드(Node)와 엣지(Edge)를 연결하여 
        전체적인 사고 흐름을 설계합니다.
        """
        workflow = StateGraph(AgentState)

        # 1. 노드 등록: 실제 수행할 함수들을 그래프에 추가합니다.
        workflow.add_node("llm_think", self.call_model)      # AI가 생각하는 단계
        workflow.add_node("execute_tools", self.execute_tools) # 도구를 실행하는 단계

        # 2. 시작점 설정: 그래프가 실행되면 llm_think 노드부터 시작합니다.
        workflow.set_entry_point("llm_think")

        # 3. 조건부 엣지 설정: llm_think가 끝나면 다음에 어디로 갈지 결정합니다.
        workflow.add_conditional_edges(
            "llm_think",
            self.should_continue,
            {
                "continue": "execute_tools", # 도구 사용이 필요하면 도구 실행 노드로
                "end": END                   # 답변이 충분하면 종료(END)로
            }
        )

        # 4. 순환 연결: 도구 실행이 끝나면 다시 모델에게 판단을 맡기기 위해 복귀합니다.
        workflow.add_edge("execute_tools", "llm_think")

        return workflow.compile()

    async def call_model(self, state: AgentState) -> Dict[str, List[BaseMessage]]:
        """
        [LLM Node] 현재까지의 대화 상태를 바탕으로 LLM에게 다음 행동을 판단하게 합니다.
        모델의 응답은 다시 메시지 리스트에 추가됩니다.
        """
        messages = state["messages"]
        
        # 시스템 프롬프트가 설정되어 있고, 대화의 처음에만 주입하여 정체성을 고정합니다.
        if self.system_prompt and not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=self.system_prompt)] + messages
            
        try:
            response = await self.llm.ainvoke(messages)
            return {"messages": [response]}
        except Exception as e:
            print(f"[ERROR] 모델 호출 중 오류 발생: {e}")
            raise e

    async def execute_tools(self, state: AgentState) -> Dict[str, List[BaseMessage]]:
        """
        [Tool Node] 모델이 '도구 호출'을 결정했을 때, 실제 파이썬 함수를 실행하고 결과를 기록합니다.
        실행 결과는 ToolMessage 형태로 반환되어 모델이 이를 인지하도록 합니다.
        """
        last_message = state["messages"][-1]
        tool_outputs = []
        
        # 모델의 응답에 담긴 모든 도구 호출 요청을 순차적으로 처리합니다.
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            if tool_name in self.tools_dict:
                action = self.tools_dict[tool_name]
                print(f"  >> 도구 실행: {tool_name}({tool_args})")
                
                output = await action.ainvoke(tool_args)
                tool_outputs.append(ToolMessage(
                    content=str(output),
                    tool_call_id=tool_call["id"]
                ))
            else:
                print(f"  >> [경고] 존재하지 않는 도구 호출 시도: {tool_name}")
                
        return {"messages": tool_outputs}

    def should_continue(self, state: AgentState) -> str:
        """
        [Router] 모델의 마지막 응답을 검사하여 도구 실행이 필요한지 판단합니다.
        도구 호출(tool_calls)이 있으면 'continue', 없으면 'end'를 반환합니다.
        """
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        return "end"

    async def run(self, user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        사용자 입력을 받아 그래프를 실행하고, 각 단계(노드)의 변화를 스트리밍합니다.
        """
        inputs = {"messages": [HumanMessage(content=user_input)]}
        async for event in self.app.astream(inputs):
            yield event
