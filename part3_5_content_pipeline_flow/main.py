# main.py
from crewai.flow.flow import Flow, listen, start, router, and_, or_
from crewai import Agent
from pydantic import BaseModel
from tools import web_search_tool
from typing import List
from crewai import LLM
from seo_crew import SeoCrew
from virality_crew import ViralityCrew


# 2026.02.26 생성
class BlogPost(BaseModel):
    title: str
    subtitle: str
    sections: List[str]
 
 
class Tweet(BaseModel):
    content: str
    hashtags: str
   
 
class LinkedInPost(BaseModel):
    content: str
    hashtags: str
    
    
class Score(BaseModel):
    score: int = 0
    reason: str = ""
    

# [상태 관리]: 파이프라인 전체에서 공유할 데이터 모델
class ContentPipelineState(BaseModel):
    # Inputs (외부에서 받아올 데이터)
    content_type: str = ""
    topic: str = ""
    
    # Internal (내부 로직용 데이터)
    max_length: int = 0
    research: str = ""
    score: Score | None = None
       
    # 최대 시도 횟수
    retry_count: int = 0
    
    # Content
    blog_post: BlogPost | None = None
    tweet: Tweet | None = None
    linkedin_post: LinkedInPost | None = None
    

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
        # 2026.02.26 생성
        researcher = Agent(
            role="Head Researcher",
            backstory="""You're like a digital detective who loves digging up fascinating facts and
            insights. You have a knack for finding the good stuff that others miss.""",
            goal=f"Find the most interesting and useful info about {self.state.topic}",
            tools=[web_search_tool]
        )
        self.state.research = researcher.kickoff(f"Find the most interesting and useful info about {self.state.topic}")
        
        return True
    
    # [@router]: 리서치 결과를 바탕으로 '어느 팀(메서드)'으로 보낼지 결정하는 분기점
    @router(conduct_research)
    def conduct_research_router(self):
        content_type = self.state.content_type
        print(f"3. Router Decision: {content_type}")
        
        if content_type == 'blog':
            return 'make_blog'
        elif content_type == 'tweet':
            return 'make_tweet'
        else:
            return 'make_linkedin_post'
    
    # --- 분기된 작업들 (Writer Agents) ---
    @listen(or_('make_blog', 'remake_blog'))
    def handle_make_blog(self):
        # if blog post has been made, show the old one to the ai and ask it to improve, else
        # just ask to create.
        print('   -> Path A: Making blog post...')
        blog_post = self.state.blog_post
        
        llm = LLM(model="openai/o4-mini", response_format=BlogPost)
        
        if blog_post is None:
            # make it
            result = llm.call(f""" 
                     make a blog post with SEO practives on the topic {self.state.topic} using the following research:
                     
                     research Starts
                     ===============
                     {self.state.research}
                     ===============
                     </research>
                     """) # type: ignore
            
        else:
            # improve it
            result = llm.call(f"""
            You wrote this blog post on {self.state.topic}, but it does not have a good SEO score.
            because of {self.state.score.reason}
            
            Imporve it.
            
            <blog post>
            {self.state.blog_post.model_dump_json()}
            </blog post>
            Use the following research. 
            
            <research>         
            ===============
            {self.state.research}
            ===============
            </research>
            """) # type: ignore
        
        # model처럼 보이는 string을 줄 건데 이걸 validate하고 나한테 model 줘, 나한테 blogpost줘 이런 의미
        # 원래 위에서 llm 호출할 때 self.state.blog_post 썻는데, 이러면 작동할 때 결과를 model인자로 안받고 str로 받아서 에러남
        # crewai 버그가 있어서 그런걸로 추측
        self.state.blog_post = result
        

    @listen(or_('make_tweet', 'remake_tweet'))
        # if tweet has been made, show the old one to the ai and ask it to improve, else
        # just ask to create.
    def handle_make_tweet(self):
        print('   -> Path B: Making tweet...')
        
        tweet = self.state.tweet
        
        llm = LLM(model="openai/o4-mini", response_format=Tweet)
        
        if tweet is None:
            # make it
            result = llm.call(f""" 
                     make a tweet that can go viral on the topic {self.state.topic} using the following research:
                     
                     research Starts
                     ===============
                     {self.state.research}
                     ===============
                     </research>
                     """) # type: ignore
            
        else:
            # improve it
            result = llm.call(f"""
            You wrote this tweet on {self.state.topic}, but it does not have a good virality score.
            because of {self.state.score.reason}
            
            Imporve it.
            
            <tweet>
            {self.state.tweet.model_dump_json()}
            </tweet>
            Use the following research. 
            
            <research>         
            ===============
            {self.state.research}
            ===============
            </research>
            """) # type: ignore
            
            self.state.tweet = result

    @listen(or_('make_linkedin_post', 'remake_linkedin'))
        # if post has been made, show the old one to the ai and ask it to improve, else
        # just ask to create.
    def handle_make_linkedin_post(self):
        print('   -> Path C: Making linkedin post...')
        
        linkedin_post = self.state.linkedin_post
        
        llm = LLM(model="openai/o4-mini", response_format=Tweet)
        
        if linkedin_post is None:
            # make it
            result = llm.call(f""" 
                     make a linkedin post that can go viral on the topic {self.state.topic} using the following research:
                     
                     research Starts
                     ===============
                     {self.state.research}
                     ===============
                     </research>
                     """) # type: ignore
            
        else:
            # improve it
            result = llm.call(f"""
            You wrote this linkedin post on {self.state.topic}, but it does not have a good virality score.
            because of {self.state.score.reason}
            
            Imporve it.
            
            <linkedin_post>
            {self.state.linkedin_post.model_dump_json()}
            </linkedin_post>
            Use the following research. 
            
            <research>         
            ===============
            {self.state.research}
            ===============
            </research>
            """) # type: ignore

            self.state.linkedin_post = result
    
    # --- 검수 및 최적화 단계 (비대칭 구조) ---
    
    # SEO = 검색 최적화, 블로그는 검색엔진 노출이 중요하니 검색 최적화 검사가 필요해서 블로그만 실행
    # @listen(handle_make_blog): 오직 '블로그 작성'이 끝났을 때만 실행됨
    @listen(handle_make_blog)
    def check_seo(self): 
        print('5-A. checking Blog SEO')
    
        result = (
            SeoCrew().crew().kickoff(inputs={
                'topic':self.state.topic,
                'blog_post':self.state.blog_post.model_dump_json(),
                }
            )
        )
        self.state.score = result.pydantic
        
            
    # '좋아요' 등 화제성 중요, 트위터랑 링크드인은 확산성 검사
    # @listen(or_...): 트윗이나 링크드인 중 '하나라도' 실행되면 작동
    @listen(or_(handle_make_tweet, handle_make_linkedin_post))
    def check_virality(self):
        print('5-B. Checking virality...')
        
        result = (
            ViralityCrew().crew().kickoff(inputs={
                'topic':self.state.topic,
                'content_type':self.state.content_type,
                'content': (self.state.tweet.model_dump_json()
                if self.state.content_type == 'tweet'
                else self.state.linkedin_post.model_dump_json())
                }
            )
        )
        self.state.score = result.pydantic
        
    @router(or_(check_seo, check_virality)) # type: ignore
    # score에 따라서 post를 다시 만들거나 tweet 다시 만들기
    def score_router(self):
        
        # content_type 추출
        content_type = self.state.content_type
        score = self.state.score
        
        # 체크
        print(f"Current Score: {score.score}, Retry Count: {self.state.retry_count}")
        
        if score.score >= 8 or self.state.retry_count >= 2:
            return 'check_passed'
        else:
            #  통과 못해서 다시 돌려보낼 때 카운트를 1 올림
            self.state.retry_count += 1 
            
            if content_type == 'blog':
                return 'remake_blog'
            elif content_type == 'linkedin':
                return 'remake_linkedin'
            else:
                return 'remake_tweet'
        
    # [최종 단계]: SEO 검사나 화제성 체크 중 하나라도 끝나면 실행
    @listen("check_passed")
    def finalize_content(self):
        """Finalize the content"""
        print("🎉 Finalizing content...")

        if self.state.content_type == "blog":
            print(f"📝 Blog Post: {self.state.blog_post.title}")
            print(f"🔍 SEO Score: {self.state.score.score}/100")
        elif self.state.content_type == "tweet":
            print(f"🐦 Tweet: {self.state.tweet}")
            print(f"🚀 Virality Score: {self.state.score.score}/100")
        elif self.state.content_type == "linkedin":
            print(f"💼 LinkedIn: {self.state.linkedin_post.title}")
            print(f"🚀 Virality Score: {self.state.score.score}/100")

        print("✅ Content ready for publication!")
        return (
            self.state.linkedin_post
            if self.state.content_type == "linkedin"
            else (
                self.state.tweet
                if self.state.content_type == "tweet"
                else self.state.blog_post
            )
        )


# [실행부]
flow = ContentPipelineFlow()

# ContentPipelineState 초기 설정 입력
# kickoff 함수가 이 딕셔너리를 받아서 자동으로 self.state(Pydantic 객체)로 변환해줌
flow.kickoff(inputs={
    "content_type": "blog",
    "topic": "2026 current kospi flow"
})

# 시각화 (선택사항)
# crewai flow 흐름도 html로 보여줌
# flow.plot()   