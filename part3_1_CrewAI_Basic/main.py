import dotenv

dotenv.load_dotenv()

from crewai import Crew, Agent, Task
# CrewBase가 프로젝트의 기본 클래스 역할
# @CrewBase가 실행되면서 현재 파일(main.py)이 CrewAI 프로젝트로 인식됨
# 같은 위치에 있는 config 폴더 내 yaml 파일들을 자동으로 불러옴
# 읽어온 내용을 self.agents_config와 self.tasks_config라는 변수에 담아서 TranslatorCrew 클래스 안에 강제로 집어넣음
from crewai.project import CrewBase, agent, task, crew 
from tools import count_letters

@CrewBase
class TranslatorCrew:
    # 여기선 3개 role, goal, backstory를 지정
    # role은 agent가 어떤 역할을 하는지
    # goal은 agent가 달성하고자 하는 목표
    # backstory는 agent의 배경 이야기
    
    # 원래는 translator_agent 하나로 영어->이탈리아어, 이탈리아어->한국어 번역을 다 처리했음
    # 이렇게 처리하면, 실행 후 터미널에서 확인할 때, 각 agent별로 메세지가 분리되지 않아서 결과 확인이 직관적이지 않음
    # 그래서 분리함
    # @agent
    # def translator_agent(self):
    #     return Agent(config = self.agents_config['translator_agent'],
    #                  )
 
    @agent
    def English_to_italian_agent(self):
        return Agent(config = self.agents_config['English_to_italian_agent'], # type: ignore
                     )
        
    @agent
    def Italian_to_korean_agent(self):
        return Agent(config = self.agents_config['Italian_to_korean_agent'], # type: ignore
                     )

    '''
    프롬프트를 잘 작성해주면 agent 성능이 좋아짐
    중요한 건 context를 잘 주는 것
    prompt는 python 코드와 분리하는 것 추천
    왜냐하면, 나중에 prompt를 수정할 때마다 코드를 수정해야 하기 때문
    config 폴더 만들고 agent.yaml, task.yaml 파일 만들어서 prompt 작성
    반드시 agent.yaml, task.yaml 파일명으로 만들어야 함
    '''
    
    @agent
    def counter_agent(self):
        return Agent(
            config = self.agents_config['counter_agent'], # type: ignore
            tools = [count_letters],       
                     )

    @task
    def translate_task(self): # 여기선 description 작성하는데, task가 완료되었을 때 결과물이 어떤 형태인지 설명하는 역할
        return Task(config=self.tasks_config['translate_task']) # type: ignore
         
    '''
    Tasks.yaml 내 Description에 {sentence}라는 변수가 있는데, 
    이 변수는 나중에 input으로 문장을 입력받아 실행할때마다 입력받는 문장을 치환해서 사용함
    이렇게 안해주고 특정 문장을 지정해주면, 매번 같은 문장만 번역하게 됨
    그래서 유연하게 하기 위해서 변수로 지정해주는 것
    '''
    
    @task
    def retranslate_task(self): # 여기선 description 작성하는데, task가 완료되었을 때 결과물이 어떤 형태인지 설명하는 역할
        return Task(config=self.tasks_config['retranslate_task']) # type: ignore

    @task
    def count_task(self): # 여기선 description 작성하는데, task가 완료되었을 때 결과물이 어떤 형태인지 설명하는 역할
        return Task(config=self.tasks_config['count_task']) # type: ignore

    @crew
    def assemble_crew(self):
        return Crew(
            agents=self.agents, # type: ignore / agent 데코레이터가 붙은 메서드들을 agents로 지정 
            tasks=self.tasks, # type: ignore / task 데코레이터가 붙은 메서드들을 tasks로 지정 
            verbose=True # type: ignore / verbose=True로 지정하면, 터미널에 실행 과정이 상세히 출력됨
        )
        

TranslatorCrew().assemble_crew().kickoff(inputs={'sentence':"I'm taejun and i like take rest at home."}) # type: ignore / kickoff 메서드로 Crew 실행