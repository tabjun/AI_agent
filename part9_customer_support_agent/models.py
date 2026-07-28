from pydantic import BaseModel
from typing import Optional

class UserAccountContext(BaseModel):
    # context는 에이전트 실행 시점에 주입되는 사용자별 런타임 데이터다.
    # 여기서는 고객지원 응답에 필요한 최소 정보만 모델로 정의한다.
    customer_id: int
    name: str
    tier: str = "basic" # premium, enterprise 등 등급에 따라 차등 혜택 받을 수 있게 구성
    # triage_agent.py의 dynamic_triage_agent_instructinos가 wrapper.context.email을 참조한다.
    # 강의 원본 models.py 기준으로 Optional[str] = None으로 추가.
    email: Optional[str] = None


class InputGuardRailOutput(BaseModel):
    
    # 정해진 주제에서 벗어난 질문인지 여부 판단
    is_off_topic: bool
    # 선정 이유
    reason: str
    

# triage_agent.py의 handle_handoff/make_handoff가 참조하는 타입명은 HandoffData(소문자 off)다.
# 클래스명이 HandOffData(대문자 O)로 어긋나 있으면 import 자체가 NameError로 깨진다.
class HandoffData(BaseModel):
    # handoff 발생 시, 어떤 에이전트에게 handoff 되었는지, 어떤 이유로 handoff 되었는지 등
    # 에이전트 간 handoff를 기록할 수 있는 데이터 모델 정의
    to_agent_name: str
    issue_type: str
    issue_description: str
    reason: str