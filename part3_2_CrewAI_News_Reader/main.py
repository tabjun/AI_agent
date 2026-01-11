import dotenv

dotenv.load_dotenv()

from crewai import Crew, Agent, Task
from crewai.project import CrewBase, agent, task, crew
from tools import search_tool, scrape_tool

@CrewBase
class NewsReaderAgent:
    
    @agent
    def news_hunter_agent(self):
        return Agent(
            config = self.agents_config['news_hunter_agent'],
            tools = [search_tool, scrape_tool],
        )
    
    @agent
    def summarizer_agent(self):
        return Agent(
            config = self.agents_config['summarizer_agent'],
            tools=[search_tool],
        )
        
    @agent
    def curator_agent(self):
        return Agent(
            config=self.agents_config['curator_agent'],
        )
    
    @task
    def content_harvesting_task(self):
        return Task(
            config=self.tasks_config['content_harvesting_task'],
        )
    
    @task
    def summarization_task(self):
        return Task(
            config=self.tasks_config['summarization_task'],
        )        
        
    @task
    def final_report_assembly_task(self):
        return Task(
            config=self.tasks_config['final_report_assembly_task'],
        )
        
    @crew
    def crew(self):
        return Crew(
            tasks=self.tasks,
            agents=self.agents,
            verbose=True,
        )
        
# NewsReaderAgent().crew().kickoff()

print("## 뉴스 요약 에이전트 시작 ##")
topic_input = input("수집하고 싶은 뉴스 주제 입력(예: AI Trends): ")

if not topic_input:
    topic_input = "AI Technology and stock trend(about QQQ, Nasdaq, S&P500, SCHG)" # 기본으로

NewsReaderAgent().crew().kickoff(inputs={"topic": topic_input})