from pydantic import BaseModel, Field
from typing import Optional

class UserAccountContext(BaseModel):
    # context는 에이전트 실행 시점에 주입되는 사용자별 런타임 데이터다.
    # 여기서는 고객지원 응답에 필요한 최소 정보만 모델로 정의한다.
    customer_id: int
    name: str
    tier: str = "basic" # premium, enterprise 등 등급에 따라 차등 혜택 받을 수 있게 구성
    # triage_agent.py의 dynamic_triage_agent_instructions가 wrapper.context.email을 참조한다.
    # 강의 원본 models.py 기준으로 Optional[str] = None으로 추가.
    email: Optional[str] = None
    # technical_agent.py의 provide_troubleshooting_steps(tools.py)가 이 필드에 이력을 쌓는다.
    troubleshooting_steps: list[str] = Field(default_factory=list)

    def is_premium_customer(self) -> bool:
        return self.tier != "basic"

    def add_troubleshooting_step(self, step: str) -> None:
        self.troubleshooting_steps.append(step)


class InputGuardRailOutput(BaseModel):
    
    # 정해진 주제에서 벗어난 질문인지 여부 판단
    is_off_topic: bool
    # 선정 이유
    reason: str
    

# output_guardrails.py의 4개 도메인 가드레일(technical/billing/order/account)이 공통으로 쓰는 스키마.
# "off_topic"이라는 이름은 input_guardrail(주제 자체가 고객지원과 무관한지)과 혼동되기 쉬워서 빼고,
# 실제로 판단해야 하는 건 "이 답변이 응답한 에이전트의 담당 도메인이 아닌 다른 도메인 정보를 새고 있는가"다.
# 예) 기술지원 답변에 결제 금액을 알려주거나, 계정 비밀번호 재설정 절차를 안내하면 담당 범위를 벗어난 것.
# 4개 필드를 한 클래스에 모아두고, 각 에이전트는 자기 도메인 필드를 제외한 나머지 3개만 검사한다
# (자기 도메인 정보를 담는 건 당연하므로 그건 트립 사유가 아니다).
class DomainLeakageGuardRailOutput(BaseModel):

    # 기술 지원 범위(진단, 트러블슈팅, 에스컬레이션)를 벗어난 내용을 포함하는지
    contains_technical_data: bool
    # 결제/구독/환불 등 청구 관련 내용을 포함하는지
    contains_billing_data: bool
    # 배송/주문 조회/반품 등 주문 관련 내용을 포함하는지
    contains_order_data: bool
    # 비밀번호 재설정/이메일 변경/계정 삭제 등 계정 관리 관련 내용을 포함하는지
    contains_account_data: bool
    # 선정 이유
    reason: str

    def leaks_outside(self, *own_domain_fields: str) -> bool:
        """own_domain_fields로 지정한 필드(자기 담당 도메인)를 제외하고,
        나머지 도메인 필드 중 하나라도 True면 담당 범위를 벗어난 것으로 판단한다."""
        other_fields = {
            "contains_technical_data",
            "contains_billing_data",
            "contains_order_data",
            "contains_account_data",
        } - set(own_domain_fields)
        return any(getattr(self, field) for field in other_fields)


# triage_agent.py의 handle_handoff/make_handoff가 참조하는 타입명은 HandoffData(소문자 off)다.
# 클래스명이 HandOffData(대문자 O)로 어긋나 있으면 import 자체가 NameError로 깨진다.
class HandoffData(BaseModel):
    # handoff 발생 시, 어떤 에이전트에게 handoff 되었는지, 어떤 이유로 handoff 되었는지 등
    # 에이전트 간 handoff를 기록할 수 있는 데이터 모델 정의
    to_agent_name: str
    issue_type: str
    issue_description: str
    reason: str