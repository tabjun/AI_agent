import dotenv
from typing import Dict, Any
dotenv.load_dotenv()

from crewai import Crew, Agent, Task, Process
from crewai.project import CrewBase, task, agent, crew
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from models import JobList, RankedJobList, ChosenJob
from tools import web_search_tool
'''
Task 끼리 연결해주는 작업을 해줘야 함
task 끼리 reference 설정
'''

resume_knowledge  = TextFileKnowledgeSource(
   file_paths=[
      'resume.txt'
   ]
)

@CrewBase
class JobHunterCrew:
   # 명시적으로 경로 지정
   # 안해도 crewai가 자동으로 agents_config, tasks_config 입력하면, 부모 폴더에서 config 폴더 찾아서 적당하게 로드해줌
   agents_config: Any = 'config/agents.yaml'
   tasks_config: Any = 'config/tasks.yaml'

   @agent
   def job_search_agent(self):
      return Agent(
         config=self.agents_config['job_search_agent'], # type: ignore
         tools=[web_search_tool]
      )
      
   @agent
   def job_matching_agent(self):
      return Agent(
         config=self.agents_config['job_matching_agent'], # type: ignore
         knowledge_sources=[resume_knowledge],
      )
      
   @agent
   def resume_optimization_agent(self):
      return Agent(
         config=self.agents_config['resume_optimization_agent'], # type: ignore
         knowledge_sources=[resume_knowledge],
      )
      
   @agent
   def company_research_agent(self):
      return Agent(
         config=self.agents_config['company_research_agent'], # type: ignore
         knowledge_sources=[resume_knowledge],
         tools=[web_search_tool], # 회사 조사에 웹 검색 도구 사용할테니 추가      
      )
      
   @agent
   def interview_prep_agent(self):
      return Agent(
         config=self.agents_config['interview_prep_agent'], # type: ignore
         knowledge_sources=[resume_knowledge],
      )
      
   @task
   def job_extraction_task(self):
      return Task(
         config=self.tasks_config['job_extraction_task'], # type: ignore
         output_pydantic=JobList,
      )
      
   @task
   def job_matching_task(self):
      return Task(
         config=self.tasks_config['job_matching_task'], # type: ignore
         output_pydantic=RankedJobList,
      )

   @task
   def job_selection_task(self):
      return Task(
         config=self.tasks_config['job_selection_task'], # type: ignore
         output_pydantic=ChosenJob,
      )

   @task
   def resume_rewriting_task(self): # job selection task 다음에 수행되는거라서 context 설정 필요 없음
      return Task(
         config=self.tasks_config['resume_rewriting_task']  # type: ignore
      )

   @task
   def company_research_task(self):
      return Task(
         config=self.tasks_config['company_research_task'], # type: ignore
         context=[self.job_selection_task()] # type: ignore
      )

   @task
   def interview_prep_task(self):
      return Task(
         config=self.tasks_config['interview_prep_task'], # type: ignore
         context=[self.job_selection_task(), # type: ignore
                  self.resume_rewriting_task(), # type: ignore
                  self.company_research_task(), # type: ignore
                  ]
      )
       
   # [새로 추가] 리포트 태스크 함수
   @task
   def report_task(self):
      return Task(
         config=self.tasks_config['report_task'],  # tasks.yaml에 추가한 이름
         context=[
             self.job_selection_task(),      # 어떤 직업 골랐는지 알아야 함
             self.resume_rewriting_task(),   # 이력서 어떻게 바꿨는지 알아야 함
             self.company_research_task(),   # 회사 조사 내용 알아야 함
             self.interview_prep_task()      # 면접 준비 내용 알아야 함
         ],
         output_file='output/process_report.md' # 파일로 저장
      )      

   @crew
   def crew(self):
      return Crew(
         agents=self.agents,# type: ignore
         tasks=self.tasks, # type: ignore
         verbose=True,
         process=Process.sequential
      )
      

JobHunterCrew().crew().kickoff(
   inputs={
      'level': 'junior',
      'position': 'Data Analyst',
      'location': 'Korea'
   }
)