import asyncio
import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, ToolMessage
from agent import LangGraphAgentEngine

# [1. 채용 특화 도구 정의]

@tool
async def search_jobs(role: str, location: str):
    """특정 역할과 지역에 맞는 채용 공고를 검색합니다."""
    print(f" (도구 실행: {location} 지역의 {role} 공고 검색 중...)")
    await asyncio.sleep(1.5)
    
    # 가상의 채용 데이터
    jobs = [
        {"title": "Senior Python Developer", "company": "TechCorp", "location": "Seoul"},
        {"title": "AI Engineer", "company": "DataMind", "location": "Pangyo"},
        {"title": "Backend Developer", "company": "CloudNine", "location": "Seoul"}
    ]
    
    filtered_jobs = [j for j in jobs if role.lower() in j["title"].lower()]
    return f"검색된 채용 정보: {filtered_jobs if filtered_jobs else '일치하는 공고가 없습니다.'}"

@tool
async def analyze_resume_fit(resume_text: str, job_description: str):
    """이력서와 채용 공고의 적합도를 분석하고 개선점을 제안합니다."""
    print(f" (도구 실행: 이력서 매칭 분석 중...)")
    await asyncio.sleep(2)
    
    # 간단한 분석 로직 시뮬레이션
    score = 85
    suggestions = ["Python 숙련도는 높으나, 클라우드 경험(AWS)을 더 강조하면 좋겠습니다."]
    
    return f"분석 결과: 적합도 {score}점. 제안사항: {suggestions}"

# [2. Job Hunter 에이전트 정체성 부여]
JOB_HUNTER_PROMPT = """
당신은 '프로페셔널 커리어 코치 및 채용 전문가'입니다.
당신의 목표는 사용자가 원하는 직무를 찾고, 그 직무에 합격할 수 있도록 이력서를 최적화하는 것을 돕는 것입니다.

[작동 절차]
1. 사용자가 구직을 원하면 'search_jobs'를 사용하여 현재 공고를 확인하세요.
2. 사용자가 이력서 분석을 요청하거나 공고에 대한 적합도를 물어보면 'analyze_resume_fit'을 사용하세요.
3. 단순히 정보를 나열하지 말고, 전문가로서의 조언(예: 면접 팁, 연봉 협상 전략 등)을 함께 제공하세요.
4. 모든 답변은 한국어로 정중하고 전문적이게 작성하세요.
"""

async def main():
    # 1. 모델 설정 (gpt-4o)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    
    # 2. 도구 구성
    tools = [search_jobs, analyze_resume_fit]
    
    # 3. 에이전트 생성
    job_agent = LangGraphAgentEngine(
        model=llm,
        tools=tools,
        system_prompt=JOB_HUNTER_PROMPT
    )
    
    # 4. 시나리오 실행
    scenario = "서울에서 파이썬 개발자 자리를 찾아보고, 내 이력서(파이썬 5년차, 장고 숙련자)가 잘 맞는지 분석해줘."
    print(f"\n[사용자 요청]: {scenario}")
    print("="*60)

    async for node, content in job_agent.run(scenario):
        print(f"\n>>> [단계: {node}]")
        messages = content.get("messages", [])
        for msg in messages:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"  [결정] '{tc['name']}' 실행 결정")
            elif isinstance(msg, ToolMessage):
                print(f"  [결과] {msg.content}")
            elif isinstance(msg, AIMessage) and msg.content:
                print(f"  [답변] {msg.content}")

    print("\n" + "="*60)
    print("채용 컨설팅이 완료되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
