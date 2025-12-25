import dotenv

dotenv.load_dotenv()

from crewai import Crew, Agent, Task
from crewai.project import CrewBase, agent, task, crew


@CrewBase
class TranslatorCrew:
    # 여기선 3개 role, goal, backstory를 지정
    # role은 agent가 어떤 역할을 하는지
    # goal은 agent가 달성하고자 하는 목표
    # backstory는 agent의 배경 이야기
 
    @agent
    def translator_agent(self):
        return Agent(config = self.agents_config['translator_agent'],
                     )

    '''
    프롬프트를 잘 작성해주면 agent 성능이 좋아짐
    중요한 건 context를 잘 주는 것
    prompt는 python 코드와 분리하는 것 추천
    왜냐하면, 나중에 prompt를 수정할 때마다 코드를 수정해야 하기 때문
    config 폴더 만들고 agent.yaml, task.yaml 파일 만들어서 prompt 작성
    반드시 agent.yaml, task.yaml 파일명으로 만들어야 함
    '''

    @task
    def translate_task(self): # 여기선 description 작성하는데, task가 완료되었을 때 결과물이 어떤 형태인지 설명하는 역할
        return Task(config=self.tasks_config['translate_task'])
         
    '''
    Tasks.yaml 내 Description에 {sentence}라는 변수가 있는데, 
    이 변수는 나중에 input으로 문장을 입력받아 실행할때마다 입력받는 문장을 치환해서 사용함
    이렇게 안해주고 특정 문장을 지정해주면, 매번 같은 문장만 번역하게 됨
    그래서 유연하게 하기 위해서 변수로 지정해주는 것
    '''
    
    @task
    def retranslate_task(self): # 여기선 description 작성하는데, task가 완료되었을 때 결과물이 어떤 형태인지 설명하는 역할
        return Task(config=self.tasks_config['retranslate_task'])

    @crew
    def assemble_crew(self):
        return Crew(
            agents=self.agents, # agent 데코레이터가 붙은 메서드들을 agents로 지정
            tasks=self.tasks, # task 데코레이터가 붙은 메서드들을 tasks로 지정
            verbose=True
        )
        

TranslatorCrew().assemble_crew().kickoff(inputs={'sentence':"I'm taejun and i like take rest at home."})