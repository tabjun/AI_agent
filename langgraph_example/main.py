import asyncio
from langchain_core.tools import tool
from agent import LangGraphAgentEngine

# [1. 기술 연구 에이전트 전용 도구 정의]
@tool
async def search_knowledge_base(query: str):
    """
    지식 베이스(가상 데이터베이스)에서 기술 문서를 상세하게 검색합니다.
    사용자가 궁금해하는 기술 스택(LangChain, LangGraph, UV 등)에 대한 정보를 제공합니다.
    """
    print(f"  [Knowledge Base] '{query}' 검색 중...")
    await asyncio.sleep(0.5) 
    
    knowledge_data = {
        "LangChain": "LangChain은 LLM을 활용한 애플리케이션 개발을 돕는 통합 프레임워크입니다.",
        "LangGraph": "LangGraph는 에이전트의 사고 흐름을 순환 그래프 구조로 설계할 수 있게 돕는 라이브러리입니다.",
        "UV": "UV는 Rust 기반의 초고속 파이썬 패키지 매니저로 pip를 대체할 수 있습니다."
    }
    
    for key, value in knowledge_data.items():
        if key.lower() in query.lower():
            return f"'{key}' 검색 결과: {value}"
            
    return f"'{query}'에 대한 정보를 찾을 수 없습니다."

@tool
async def create_summary_report(content: str):
    """
    수집된 기술 정보들을 분석하여 가시성 좋은 전문적인 리포트 형식으로 요약합니다.
    정보가 방대할 때 사용자의 이해를 돕기 위해 사용됩니다.
    """
    print(f"  [Reporter] 정보 가공 및 보고서 생성 중...")
    await asyncio.sleep(0.8)
    return f"--- 기술 분석 리포트 ---\n[핵심 요약]: {content[:100]}...\n[결론]: 전문가 검토 및 분석 완료."

# [2. 전문가 페르소나 설정]
SYSTEM_PROMPT = """
당신은 '글로벌 IT 기술 전문 연구원'입니다.
사용자의 질문에 대해 지식 베이스를 철저히 조사하고 전문적인 보고서 형식으로 답하세요.
반드시 'search_knowledge_base'를 먼저 사용하고, 결과가 나오면 'create_summary_report'로 정리하십시오.
"""

async def start_research():
    """연구 에이전트를 초기화하고 실행하는 메인 함수입니다."""
    researcher = LangGraphAgentEngine(
        tools=[search_knowledge_base, create_summary_report],
        system_prompt=SYSTEM_PROMPT
    )
    
    user_question = "LangGraph와 UV에 대해 조사해서 보고서로 만들어줘."
    print(f"\n[사용자 요청]: {user_question}")
    print("="*60)

    async for event in researcher.run(user_question):
        for node_name, content in event.items():
            print(f"\n>>> 현재 단계: {node_name}")
            for msg in content.get("messages", []):
                if msg.content:
                    print(f"  [{type(msg).__name__}]: {msg.content[:150]}...")

    print("\n" + "="*60)
    print("기술 연구 업무가 모두 종료되었습니다.")

# uv run main.py 시 즉시 실행 (if __name__ 제거)
asyncio.run(start_research())
