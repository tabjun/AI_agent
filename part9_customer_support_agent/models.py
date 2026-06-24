from pydantic import BaseModel

class UserAccountContext(BaseModel):
    # context는 에이전트 실행 시점에 주입되는 사용자별 런타임 데이터다.
    # 여기서는 고객지원 응답에 필요한 최소 정보만 모델로 정의한다.
    customer_id: int
    name: str
    tier: str = "basic" # premium, enterprise 등 등급에 따라 차등 혜택 받을 수 있게 구성
    
