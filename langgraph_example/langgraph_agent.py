import asyncio
import operator
import os
from typing import Annotated, TypedDict, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END

load_dotenv()

# 1. State 정의 (기억 저장소)
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

@tool
def search_db(query: str):
    """데이터베이스를 조회합니다."""
    return f"DB 결과: {query}는 매우 중요한 기술입니다."

# 2. 노드 및 로직 정의
class GraphAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o").bind_tools([search_db])
        self.workflow = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("agent", self.call_model)
        graph.set_entry_point("agent")
        graph.add_edge("agent", END) # 단순화를 위해 바로 종료
        return graph.compile()

    async def call_model(self, state: AgentState):
        res = await self.llm.ainvoke(state["messages"])
        return {"messages": [res]}

async def main():
    agent = GraphAgent()
    inputs = {"messages": [HumanMessage(content="DB에서 LangGraph 찾아줘")]}
    async for event in agent.workflow.astream(inputs):
        print(event)

if __name__ == "__main__":
    asyncio.run(main())
