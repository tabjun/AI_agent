import asyncio
from langchain_core.tools import tool
from agent import LangGraphAgentEngine

# [1. 채용 컨설턴트 전용 도구 정의]
@tool
async def search_jobs(role: str, location: str = "서울"):
    """
    사용자가 원하는 직무명과 지역을 기반으로 현재 채용 중인 공고 목록을 검색합니다.
    """
    print(f"  [Recruiter] {location} 지역의 {role} 공고를 찾는 중...")
    await asyncio.sleep(1.0)
    
    jobs_db = [
        {"title": "Senior Python Backend Developer", "company": "AI Tech", "location": "서울"},
        {"title": "AI/ML Engineer", "company": "DataFlow", "location": "판교"}
    ]
    
    matches = [j for j in jobs_db if role.lower() in j["title"].lower()]
    return f"검색된 공고 목록: {matches if matches else '일치하는 공고가 없습니다.'}"

@tool
async def analyze_resume_fit(resume_text: str, job_requirements: str):
    """
    구직자의 이력서와 직무 요구사항을 대조하여 적합도 점수와 개선 방향을 제안합니다.
    """
    print(f"  [Career Coach] 이력서 매칭 분석 중...")
    await asyncio.sleep(1.2)
    
    score = 92 if "파이썬" in resume_text else 45
    advice = "충분히 훌륭합니다!" if score > 80 else "기술 스택 보강이 필요합니다."
    return f"분석 결과: 적합도 {score}점 / 전문가 조언: {advice}"

# [2. 전문가 페르소나 설정]
COACH_PROMPT = """
당신은 '15년차 베테랑 커리어 코치 및 채용 전문가'입니다.
사용자의 성공적인 이직을 위해 채용 공고를 검색하고 이력서 분석을 수행하세요.
최종 응답에는 면접 팁과 같은 전문가적 조언을 포함하십시오.
"""

async def start_consulting():
    """채용 컨설팅 에이전트 실행 함수입니다."""
    career_coach = LangGraphAgentEngine(
        tools=[search_jobs, analyze_resume_fit],
        system_prompt=COACH_PROMPT
    )
    
    user_input = "서울에서 파이썬 백엔드 개발자 자리를 찾아줘. 내 이력서는 '파이썬 기반 API 개발 5년'이야."
    print(f"\n[사용자 요청]: {user_input}")
    print("="*60)

    async for event in career_coach.run(user_input):
        for node_name, content in event.items():
            print(f"\n>>> [단계: {node_name}]")
            for msg in content.get("messages", []):
                if msg.content:
                    print(f"  [응답] {msg.content[:150]}...")

    print("\n" + "="*60)
    print("채용 컨설팅 업무가 모두 종료되었습니다.")

# uv run job_hunter.py 시 즉시 실행 (if __name__ 제거)
asyncio.run(start_consulting())
