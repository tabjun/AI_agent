import dotenv
from typing import Dict, Any
dotenv.load_dotenv()

from crewai import Crew, Agent, Task
from crewai.project import CrewBase, task, agent, crew

'''
Task 끼리 연결해주는 작업을 해줘야 함
task 끼리 reference 설정
'''

@CrewBase
class JobHunterCrew:
   agents_config: Any = 'config/agents.yaml'
   tasks_config: Any = 'config/tasks.yaml'

   @agent
   def job_search_agent(self):
      return Agent(
         config=self.agents_config['job_search_agent'] # type: ignore
      )
      
   @agent
   def job_matching_agent(self):
      return Agent(
         config=self.agents_config['job_matching_agent'] # type: ignore
      )
      
   @agent
   def resume_optimization_agent(self):
      return Agent(
         config=self.agents_config['resume_optimization_agent'] # type: ignore
      )
      
   @agent
   def company_research_agent(self):
      return Agent(
         config=self.agents_config['company_research_agent'] # type: ignore
      )
      
   @agent
   def interview_prep_agent(self):
      return Agent(
         config=self.agents_config['interview_prep_agent'] # type: ignore
      )
      
   @task
   def job_extraction_task(self):
      return Task(
         config=self.tasks_config['job_extraction_task'] # type: ignore
      )
      
   @task
   def job_matching_task(self):
      return Task(
         config=self.tasks_config['job_matching_task'] # type: ignore
      )

   @task
   def job_selection_task(self):
      return Task(
         config=self.tasks_config['job_selection_task'] # type: ignore
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
      
   @crew
   def crew(self):
      return Crew(
         agents=self.agents,# type: ignore
         tasks=self.tasks, # type: ignore
         verbose=True,
      )
      

JobHunterCrew().crew().kickoff()