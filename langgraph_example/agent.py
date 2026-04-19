import asyncio
import operator
import os
from typing import Annotated, TypedDict, Union, List, Dict, Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# .env 파일 로드
load_dotenv()
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END

# [1. 상태 정의] 
# 그래프 내의 모든 노드가 공유하는 '데이터 바구니'입니다.
class AgentState(TypedDict):
    # Annotated와 operator.add를 사용하여 메시지가 계속 누적되도록 설정합니다.
    messages: Annotated[list[BaseMessage], operator.add]

# [2. 에이전트 엔진 클래스]
# 이 클래스는 LangGraph의 핵심 로직을 캡슐화합니다.
# 어떤 모델과 도구를 사용하든 이 엔진을 통해 그래프를 생성할 수 있습니다.
class LangGraphAgentEngine:
    def __init__(self, model, tools: List[Any], system_prompt: str = ""):
        # 모델에 도구 바인딩 및 시스템 프롬프트 설정
        self.system_prompt = system_prompt
        self.model = model.bind_tools(tools)
        self.tools_dict = {t.name: t for t in tools}
        
        # 그래프 구축
        self.app = self._build_graph()

    def _build_graph(self):
        """내부적으로 StateGraph를 구축하고 컴파일합니다."""
        workflow = StateGraph(AgentState)

        # 노드 추가
        workflow.add_node("llm_think", self.call_model)
        workflow.add_node("execute_tools", self.execute_tools)

        # 흐름 설정
        workflow.set_entry_point("llm_think")
        
        # 조건부 엣지: LLM이 도구 호출을 결정했는지 확인
        workflow.add_conditional_edges(
            "llm_think",
            self.should_continue,
            {
                "continue": "execute_tools",
                "end": END
            }
        )

        # 도구 실행 후 다시 LLM의 판단을 받기 위해 복귀
        workflow.add_edge("execute_tools", "llm_think")

        return workflow.compile()

    async def call_model(self, state: AgentState):
        """LLM에게 현재 상황을 전달하고 판단을 요청합니다."""
        messages = state['messages']
        
        # 시스템 프롬프트가 있고 대화 시작 시점에만 주입하거나, 
        # 혹은 매번 앞에 붙여서 모델의 정체성을 유지합니다.
        if self.system_prompt and not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=self.system_prompt)] + messages
            
        response = await self.model.ainvoke(messages)
        return {"messages": [response]}

    async def execute_tools(self, state: AgentState):
        """모델이 요청한 도구들을 실제로 실행합니다."""
        last_message = state['messages'][-1]
        tool_outputs = []
        
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # 도구 찾기 및 실행
            if tool_name in self.tools_dict:
                action = self.tools_dict[tool_name]
                output = await action.ainvoke(tool_args)
                tool_outputs.append(ToolMessage(
                    content=str(output),
                    tool_call_id=tool_call["id"]
                ))
        return {"messages": tool_outputs}

    def should_continue(self, state: AgentState):
        """도구 호출 여부에 따라 루프를 결정합니다."""
        last_message = state['messages'][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        return "end"

    async def run(self, user_input: str):
        """에이전트를 실행하고 결과를 스트리밍합니다."""
        inputs = {"messages": [HumanMessage(content=user_input)]}
        
        async for event in self.app.astream(inputs):
            for node_name, content in event.items():
                yield node_name, content
