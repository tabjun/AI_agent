import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from agent import LangGraphAgentEngine

# .env 로드
load_dotenv()

# [1. 특화된 도구 정의]
# 이 에이전트가 사용할 수 있는 전문적인 기술(Skill)들입니다.

@tool
async def search_knowledge_base(query: str):
    """지식 베이스(가상)에서 관련 기술 문서를 검색합니다."""
    # 실제로는 벡터 DB나 API 호출이 들어가는 자리입니다.
    print(f" (도구 실행: {query} 검색 중...)")
    await asyncio.sleep(1)
    
    knowledge_data = {
        "LangChain": "LangChain은 LLM을 활용한 애플리리케이션 개발 프레임워크입니다.",
        "LangGraph": "LangGraph는 상태를 가진 다중 에이전트 워크플로우를 구축하기 위한 라이브러리입니다.",
        "CrewAI": "CrewAI는 역할 기반 자율 AI 에이전트 협업을 위한 프레임워크입니다."
    }
    
    for key, value in knowledge_data.items():
        if key.lower() in query.lower():
            return f"[{key}에 대한 검색 결과]: {value}"
    
    return "관련된 정보를 지식 베이스에서 찾을 수 없습니다."

@tool
async def create_summary_report(content: str):
    """수집된 정보를 바탕으로 요약 보고서를 작성합니다."""
    print(f" (도구 실행: 보고서 작성 중...)")
    await asyncio.sleep(1)
    return f"--- 요약 보고서 ---\n본문: {content[:50]}...\n상태: 작성이 완료되었습니다."

# [2. 에이전트 역할 부여 (System Prompt)]
SYSTEM_PROMPT = """
당신은 '기술 문서 연구 및 요약 전문가'입니다.
당신의 역할은 사용자의 질문에 대해 지식 베이스를 검색하고, 
필요하다면 그 내용을 요약하여 보고서 형태로 제공하는 것입니다.

[작동 지침]
1. 사용자가 특정 기술에 대해 물어보면 'search_knowledge_base' 도구를 먼저 사용하세요.
2. 검색 결과를 확인한 후, 내용이 방대하다면 'create_summary_report' 도구를 사용하여 정리하세요.
3. 항상 친절하고 전문적인 어조를 유지하세요.
4. 검색 결과가 없을 경우, 아는 범위 내에서 답변하되 출처가 불분명함을 명시하세요.
"""

async def main():
    # 1. 모델 설정
    # OPENAI_API_KEY 환경변수가 설정되어 있어야 합니다.
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # 2. 도구 셋업
    tools = [search_knowledge_base, create_summary_report]
    
    # 3. 에이전트 엔진 초기화 (agent.py의 skeleton 사용)
    # 이 부분이 바로 '뼈대(Engine)' 위에 '영혼(Prompt & Tools)'을 불어넣는 과정입니다.
    research_agent = LangGraphAgentEngine(
        model=llm, 
        tools=tools, 
        system_prompt=SYSTEM_PROMPT
    )
    
    # 4. 에이전트 실행 및 결과 시각화
    user_question = "LangGraph가 무엇인지 지식 베이스에서 찾아서 요약 보고서로 만들어줘."
    print(f"\n[사용자 질문]: {user_question}")
    print("="*50)

    async for node, content in research_agent.run(user_question):
        print(f"\n>>> 현재 단계: {node}")
        
        # 메시지 내역 출력 (마지막 추가된 메시지만 확인)
        messages = content.get("messages", [])
        for msg in messages:
            if isinstance(msg, AIMessage):
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        print(f"  - AI의 결정: '{tc['name']}' 도구 호출 (인자: {tc['args']})")
                if msg.content:
                    print(f"  - AI의 답변: {msg.content}")
            
            elif isinstance(msg, ToolMessage):
                print(f"  - 도구 실행 완료! 결과: {msg.content}")

    print("\n" + "="*50)
    print("에이전트 업무가 모두 종료되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
