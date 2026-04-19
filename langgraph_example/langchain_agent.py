import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

load_dotenv()

@tool
def get_info(query: str):
    """정보를 검색합니다."""
    return f"'{query}'에 대한 검색 결과입니다."

async def main():
    llm = ChatOpenAI(model="gpt-4o")
    tools = [get_info]
    
    # LangChain 표준 프롬프트 설정
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 유능한 조수입니다."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # Agent 생성 (LangChain 방식)
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # 실행
    result = await agent_executor.ainvoke({"input": "LangChain에 대해 알려줘"})
    print(f"최종 결과: {result['output']}")

if __name__ == "__main__":
    asyncio.run(main())
