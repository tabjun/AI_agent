import asyncio
import operator
from typing import Annotated, TypedDict, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END

# 환경 변수 로드
load_dotenv()

class SimpleState(TypedDict):
    """
    LangGraph의 핵심인 상태(State) 정의입니다.
    messages 리스트는 모든 노드에서 공유되며, 대화의 맥락을 유지합니다.
    """
    messages: Annotated[List[BaseMessage], operator.add]

@tool
def mini_search(query: str):
    """단순 DB 조회 도구입니다."""
    return f"데이터베이스에서 '{query}'에 대한 정보를 발견했습니다."

class MiniGraph:
    """
    LangGraph의 최소 단위 구현 예시입니다. 
    상태 머신의 기본 구조(노드 등록 및 시작점 설정)를 보여줍니다.
    """
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o").bind_tools([mini_search])
        self.workflow = self._build()

    def _build(self):
        # 그래프 생성 및 노드/엣지 정의
        graph = StateGraph(SimpleState)
        graph.add_node("agent", self.call_llm)
        graph.set_entry_point("agent")
        graph.add_edge("agent", END) # 도구 사용 없이 즉시 종료되는 단순 예시
        return graph.compile()

    async def call_llm(self, state: SimpleState):
        """LLM을 호출하여 상태를 업데이트하는 노드 함수입니다."""
        res = await self.llm.ainvoke(state["messages"])
        return {"messages": [res]}

async def start_langgraph_mini():
    """LangGraph 미니 에이전트 실행 함수입니다."""
    graph_app = MiniGraph()
    inputs = {"messages": [HumanMessage(content="DB에서 최신 AI 트렌드 찾아줘")]}
    
    print("\n--- LangGraph 미니 예제 실행 ---")
    async for event in graph_app.workflow.astream(inputs):
        print(f"진행 이벤트: {event}")

# uv run langgraph_agent.py 시 즉시 실행 (if __name__ 제거)
asyncio.run(start_langgraph_mini())
