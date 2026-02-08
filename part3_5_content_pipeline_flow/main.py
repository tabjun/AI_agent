# main.py
from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel

# [상태 관리]: 파이프라인 전체에서 공유할 데이터 모델
class ContentPipelineState(BaseModel):
    # Inputs (외부에서 받아올 데이터)
    content_type: str = ""
    topic: str = ""
    
    # Externals (내부 로직용 데이터)
    max_length: int = 0

class ContentPipelineFlow(Flow[ContentPipelineState]):
    
    # [@start]: 공장 가동! 가장 먼저 실행되어 유효성을 검사하고 초기 설정을 잡습니다.
    @start() 
    def init_content_pipeline(self):
        print("1. Start Flow: Validating inputs...")
        
        # state를 검증하는 방식
        if self.state.content_type not in ['tweet', 'blog', 'linkedin']:
            raise ValueError('The content type is wrong')
        
        # self.state.topic으로 접근해야 함 (Pydantic 모델 안에 있으므로)
        if self.state.topic == '':
            raise ValueError("The topic can't be blank.")

        # 위 if문 즉, 검증을 거친 후 조건에 맞게 state 초기화
        if self.state.content_type == 'tweet':
            self.state.max_length = 150
        elif self.state.content_type == 'blog':
            self.state.max_length = 800
        elif self.state.content_type == 'linkedin':
            self.state.max_length = 500
        
    # [@listen]: 트윗을 쓰든, 블로그 글을 쓰든 뭘 하던 우선 주제를 알아야 함.
    # init 단계가 끝나야 리서치를 시작함.
    @listen(init_content_pipeline)
    def conduct_research(self):
        print('2. Researching....')
        return True
    
    # [@router]: 리서치 결과를 바탕으로 '어느 팀(메서드)'으로 보낼지 결정하는 분기점
    @router(conduct_research)
    def router(self):
        content_type = self.state.content_type
        print(f"3. Router Decision: {content_type}")
        
        if content_type == 'blog':
            return 'make_blog'
        elif content_type == 'tweet':
            return 'make_tweet'
        else:
            return 'make_linkedin_post'
    
    # --- 분기된 작업들 (Writer Agents) ---
    @listen('make_blog')
    def handle_make_blog(self):
        print('   -> Path A: Making blog post...')

    @listen('make_tweet')
    def handle_make_tweet(self):
        print('   -> Path B: Making tweet...')

    @listen('make_linkedin_post')
    def handle_make_linkedin_post(self):
        print('   -> Path C: Making linkedin post...')
        
    
    # --- 검수 및 최적화 단계 (비대칭 구조) ---
    
    # SEO = 검색 최적화, 블로그는 검색엔진 노출이 중요하니 검색 최적화 검사가 필요해서 블로그만 실행
    # @listen(handle_make_blog): 오직 '블로그 작성'이 끝났을 때만 실행됨
    @listen(handle_make_blog)
    def check_seo(self): 
        print('5-A. checking Blog SEO')
        
    # '좋아요' 등 화제성 중요, 트위터랑 링크드인은 확산성 검사
    # @listen(or_...): 트윗이나 링크드인 중 '하나라도' 실행되면 작동
    @listen(or_(handle_make_tweet, handle_make_linkedin_post))
    def check_virality(self):
        print('5-B. Checking virality...')
        
    # [최종 단계]: SEO 검사나 화제성 체크 중 하나라도 끝나면 실행
    @listen(or_(check_virality, check_seo))
    def finalize_content(self):
        print('6. Finalizing content: Ready to publish!')

# [실행부]
flow = ContentPipelineFlow()

# ContentPipelineState 초기 설정 입력
# kickoff 함수가 이 딕셔너리를 받아서 자동으로 self.state(Pydantic 객체)로 변환해줌!
flow.kickoff(inputs={
    "content_type": "tweet",
    "topic": "AI Dog Training"
})

# 시각화 (선택사항)
# crewai flow 흐름도 html로 보여줌
flow.plot()