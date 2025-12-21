# 🤖 AI Agents Masterclass: From Concept to Deployment

![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/GenAI-OpenAI%20%7C%20Google-green?logo=openai&logoColor=white)
![Frameworks](https://img.shields.io/badge/Frameworks-LangGraph%20%7C%20CrewAI%20%7C%20AutoGen-orange)
![Deploy](https://img.shields.io/badge/Deploy-FastAPI%20%7C%20Streamlit-purple?logo=fastapi&logoColor=white)

**[Nomad Coders AI Agents Masterclass](https://nomadcoders.co/ai-agents-masterclass/lobby)** 학습 기록 및 프로젝트 저장소입니다.

단순한 LLM 호출을 넘어, 스스로 사고하고(Think), 도구를 사용하며(Act), 다른 에이전트와 협업하여 복잡한 과업을 수행하는 **Autonomous AI Agent**의 A to Z 구현 내용 기록입니다.

---

## 🧠 Core Concept: The Agent Loop

모든 에이전트의 핵심인 **"사고-행동-관찰(Think-Act-Observe)"** 루프 구현 및 이해

1.  **Brain (Decide)**: 대화 맥락을 파악하고 도구 사용 여부를 판단 (Routing)
2.  **Hand (Act)**: 실제 함수(API, Web Search, Code Execution)를 실행
3.  **Memory (Context)**: 대화 흐름과 실행 결과를 기억하여 지속적인 상호작용 유지

---

## 📚 Curriculum & Projects Overview

### 🏗️ Part 1: Fundamentals (Lectures #0 - #2)
**Native Python**과 **OpenAI API**만으로 프레임워크 없는 순수 에이전트 원리 구현
- **Environment Setup**: `uv` 패키지 매니저 및 Python 3.13 환경 구축
- **Your First Agent**: Function Calling을 이용한 도구(Tool) 연결 및 메모리 시스템 구현

### 🚣 Part 2: CrewAI Framework (Lectures #3 - #5)
역할(Role)이 부여된 에이전트들이 팀을 이뤄 과업을 수행하는 구조 학습
- **News Reader Agent**: 커스텀 도구를 활용하여 최신 뉴스를 수집하고 요약
- **Job Hunter Agent**: 구직 사이트(Firecrawl)를 검색하여 채용 공고를 구조화된 데이터로 추출
- **Content Pipeline Agent**: `주제 선정 → 초안 작성 → 검수(Human Feedback)`로 이어지는 글쓰기 자동화 파이프라인

### 🤖 Part 3: AutoGen Framework (Lecture #6)
마이크로소프트의 AutoGen을 활용하여 다수의 에이전트가 대화하듯 협업하는 방식 학습
- **Grok Deep Research Agent**: 특정 주제에 대해 심층 탐구하는 연구원 팀(Researcher, Reviewer) 구현

### 🧩 Part 4: OpenAI Agents SDK (Lectures #7 - #9)
OpenAI의 최신 기능을 활용하여 멀티모달 및 안전한 에이전트를 구축합니다.
- **ChatGPT Clone**: 웹 검색, 파일 검색, 이미지 생성(DALL-E), 코드 인터프리터 기능 통합
- **Customer Support Agent**: 고객 응대 시나리오, 상담원 연결(Handoff), 가드레일(Guardrails)을 통한 입출력 안전 장치 구현

### 🇬 Part 5: Google ADK (Lectures #10 - #12)
Google의 Agent Development Kit를 활용하여 확장성 있는 에이전트 생태계 학습
- **Financial Advisor**: 주식 시장 데이터를 실시간 분석하고 투자 전략을 제안하는 금융 비서
- **Youtube Shorts Maker**:
    - `기획(Planner) → 프롬프트 작성 → 이미지 생성 → 오디오(Narration) → 영상 합성`
    - 멀티미디어 생성 파이프라인을 완전 자동화하는 복합 에이전트

### 🕸️ Part 6: LangGraph (Lectures #13 - #15)
복잡한 상태(State) 관리와 흐름 제어가 가능한 LangChain의 그래프 기반 프레임워크 학습
- **LangGraph Basics**: Node, Edge, State 관리 및 조건부 분기(Conditional Edges) 학습
- **Youtube Thumbnail Maker**:
    - 영상 오디오 추출/요약 → 썸네일 스케치 → 고화질 썸네일 생성
    - **Human-in-the-loop**: 중간 단계에서 사용자가 개입하여 피드백을 반영하는 상호작용 구현

### 🏛️ Part 7: Advanced Architectures & Deployment (Lectures #16 - #21)
고급 디자인 패턴을 익히고, 실제 서비스로 배포(Deployment)하는 최종 단계입니다.
- **Workflow Patterns**: Prompt Chaining, Routing, Parallelization, Orchestrator-Workers 패턴 실습
- **Multi-Agent Systems**: Supervisor(관리자)가 하위 에이전트를 조율하는 계층형 구조
- **Tutor Agent**: 파인만 기법(Feynman Technique)을 적용한 교육용 챗봇 (퀴즈 및 평가 기능)
- **A2A (Agent to Agent)**: 서로 다른 서버에 있는 에이전트끼리 통신하며 협업하는 시스템 구축
- **Deployment**: **FastAPI** 서버 구축, **Streamlit** UI 연동 및 실제 프로덕션 환경 배포

---

## 🛠 Tech Stack

- **Languages**: Python 3.13+
- **LLMs**: OpenAI GPT-4o, Google Gemini
- **Frameworks & Libraries**:
    - `OpenAI SDK`, `Google ADK`
    - `LangGraph`, `LangChain`
    - `CrewAI`, `AutoGen`
    - `Pydantic` (Data Validation)
- **Tools & APIs**: `Tavily` (Search), `Firecrawl` (Scraping), `DALL-E` (Image)
- **Deployment**: `FastAPI`, `Streamlit`, `Uvicorn`
- **Environment**: `uv` (Package Manager)

## 🚀 How to Run

1. **Clone the repository**
   ```bash
   git clone [https://github.com/tabjun/AI_agent.git](https://github.com/tabjun/AI_agent.git)
   cd AI_agent

