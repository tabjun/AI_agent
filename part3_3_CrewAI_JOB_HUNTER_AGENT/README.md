# 🤖 AI Job Search & Career Coach (CrewAI)

> **"나만의 AI 헤드헌터 & 커리어 코치 팀"** > 사용자의 이력서와 희망 조건을 기반으로 **채용 공고 검색, 적합도 분석, 이력서 첨삭, 기업 분석, 면접 준비**까지의 전 과정을 자동화하는 Multi-Agent 시스템입니다.

---

## 📋 프로젝트 개요 (Overview)

이 프로젝트는 **[CrewAI](https://www.crewai.com/)** 프레임워크를 활용하여 5명의 AI 에이전트가 유기적으로 협업하는 파이프라인을 구축했습니다.  
단순히 공고를 나열하는 것이 아니라, 내 **이력서(Resume)** 와의 연관성을 분석하고 합격 확률을 높이기 위한 구체적인 전략을 제시합니다.

### 🎯 핵심 기능
1. **Smart Search**: 희망 직무/지역/연차에 맞는 공고 자동 수집
2. **Resume Matching**: 내 이력서와 공고 간의 적합도(Match Score 1~5) 평가 및 피드백
3. **Resume Optimization**: 선정된 직무에 맞춰 이력서 내용 재구성 (Rewriting)
4. **Deep Company Research**: 지원 기업의 최신 뉴스, 비전, 면접 예상 질문 분석
5. **Interview Strategy**: 위 모든 정보를 종합한 맞춤형 면접 가이드북 생성

---

## 🔄 워크플로우 (Architecture & Data Pipeline)

이 시스템의 핵심은 각 Task가 독립적이지 않고, 앞 단계의 결과물(Output)을 다음 단계의 입력(Input)으로 사용하는 **'이어달리기(Relay)'** 구조라는 점입니다.

```mermaid
graph TD
    User((User Input)) --> A
    
    subgraph "Phase 1: Discovery"
    A[🔍 Job Search Agent] -->|Raw Job List| B[⚖️ Job Matching Agent]
    B -->|Ranked Jobs| C[✅ Job Selection Task]
    end
    
    subgraph "Phase 2: Strategy"
    C -->|Selected Job| D[📝 Resume Optimization Agent]
    C -->|Selected Job| E[🏢 Company Research Agent]
    end
    
    subgraph "Phase 3: Preparation"
    D -->|Rewritten Resume| F[🎤 Interview Prep Agent]
    E -->|Company Report| F
    end
    
    F --> Final[📄 Interview Prep.md]