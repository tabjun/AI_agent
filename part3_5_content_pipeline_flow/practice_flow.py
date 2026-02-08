# practice_flow.py
from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel

# [1. 상태 저장소 (State)]
# Flow 전체에서 공유되는 '배낭'입니다.
# kickoff(inputs={...}) 할 때 여기 정의된 변수들에 값이 자동으로 채워집니다.
class MyFirstFlowState(BaseModel):
    user_id: int = 1         # 기본값 1 (입력 없으면 1)
    is_admin: bool = False   # 기본값 False

class MyFirstFlow(Flow[MyFirstFlowState]):
    
    # [2. 시작점 (@start)]
    # Flow가 시작되면 무조건 가장 먼저 실행됩니다.
    @start()
    def first(self):
        # self.state: CrewAI가 만들어준 배낭(객체). 점(.)으로 접근 가능
        print(f"1. First step - Current User: {self.state.user_id}")
        
    # [3. 직렬 연결 (@listen)]
    # 'first'가 끝나야만 실행됩니다.
    @listen(first)
    def second(self):
        # 배낭 안의 값을 수정하면, 다른 함수들도 바뀐 값을 보게 됩니다. (상태 공유)
        self.state.user_id = 2 
        print(f"2. Second step - User ID updated to: {self.state.user_id}")
        
    # [4. 병렬 실행 (@listen)]
    # 얘도 'first'가 끝나면 실행됩니다. 
    # 즉, 'second'와 'third'는 동시에(병렬로) 달립니다. 누가 먼저 끝날지 모릅니다.
    @listen(first)
    def third(self):
        print("2. Third step (Running parallel with Second)")
        
    # [5. 동기화/합류 (and_)]
    # 'second'와 'third'가 *모두* 끝나야 실행됩니다. (Wait for All)
    # 흩어졌던 작업 흐름을 하나로 모으는 곳입니다.
    @listen(and_(second, third))
    def final(self):
        print("3. Final step - Both parallel tasks finished :)")
        
    # [6. 라우터/분기점 (@router)]
    # 'final'이 끝난 직후 실행되어, 다음 갈 길(함수 이름)을 정해줍니다.
    # Flow의 '신호등' 역할입니다.
    @router(final)
    def route(self):
        # 배낭(state)에 있는 값을 보고 판단
        if self.state.is_admin:
            return 'even' # 'even'이라는 이름의 이벤트를 발생시킴
        else:
            return 'odd'  # 'odd'라는 이름의 이벤트를 발생시킴
    
    # [7. 분기된 경로 A]
    # 라우터가 'even'이라고 했을 때만 실행됨
    @listen('even')
    def handle_even(self):
        print("4. Result: Admin Access (Even path)")
        
    # [7. 분기된 경로 B]
    # 라우터가 'odd'라고 했을 때만 실행됨
    @listen('odd')
    def handle_odd(self):
        print("4. Result: User Access (Odd path)")


# [실행부]
flow = MyFirstFlow()

# Case 1: 일반 유저 (기본값)
print("--- Case 1: Default ---")
flow.kickoff() 

# Case 2: 관리자 (입력 주입)
# inputs에 넣은 값이 MyFirstFlowState에 자동으로 매핑됩니다.
print("\n--- Case 2: Admin Input ---")
flow.kickoff(inputs={"is_admin": True, "user_id": 99})