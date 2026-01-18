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

# 🔄 AI Job Search Workflow: 데이터 연결 흐름도

이 프로젝트의 핵심은 각 Task가 독립적으로 끝나는 것이 아니라, 
앞 단계의 결과물(Output)을 뒷 단계의 입력물(Input)로 넘겨주는 '이어달리기' 구조라는 점입니다.

---

## 📊 한눈에 보는 연결 구조 (Pipeline Visualization)

[1. 공고 검색] ➔ [2. 적합도 평가] ➔ [3. 최종 1픽 선정]
                                         ⬇️
                           (선정된 공고 데이터를 기준으로 분기)
                                 ↙️               ↘️
                 [4. 이력서 수정]               [5. 기업 분석]
                                 ↘️               ↙️
                           (모든 정보를 취합하여 최종 생성)
                                         ⬇️
                              [6. 면접 준비 가이드]

---

## 🔗 단계별 연결 상세 설명 (Connection Logic)

### 1️⃣ Job Extraction (검색) ➔ Job Matching (평가)
* **연결 고리:** `Job List` (전체 공고 목록)
* **왜 연결하나요?:** 검색 에이전트가 인터넷에서 긁어온 '날것의 공고 리스트'를 넘겨줘야, 평가 에이전트가 내 이력서와 비교해서 점수를 매길 수 있습니다.

### 2️⃣ Job Matching (평가) ➔ Job Selection (선정)
* **연결 고리:** `Ranked Job List` (점수와 이유가 포함된 공고 목록)
* **왜 연결하나요?:** 평가 에이전트가 1~5점 점수를 매겨놓은 성적표를 넘겨줘야, 선정 에이전트가 그중에서 "이게 베스트다!" 하고 딱 하나(Chosen Job)를 고를 수 있습니다.

### 3️⃣ Job Selection (선정) ➔ Resume Rewrite & Company Research (분기점)
* **연결 고리:** `Chosen Job` (최종 선정된 단 하나의 공고)
* **왜 연결하나요?:** 여기가 가장 중요합니다. 타겟팅할 회사가 정해져야,
    1.  이력서 수정 에이전트가 "그 회사 JD에 맞춰서" 이력서를 고칠 수 있고,
    2.  기업 분석 에이전트가 "그 회사를" 조사할 수 있습니다.

### 4️⃣ All Previous Outputs ➔ Interview Prep (종합)
* **연결 고리:** `Chosen Job` + `Rewritten Resume` + `Company Research`
* **왜 연결하나요?:** 마지막 면접 코치는 앞선 모든 결과물을 종합해야 합니다.
    * "어떤 직무인가?" (Chosen Job)
    * "내 수정된 이력서는 어떤가?" (Rewritten Resume)
    * "회사는 어떤 곳인가?" (Company Research)
    이 3가지를 다 알아야 완벽한 면접 예상 질문과 답변 전략을 짤 수 있기 때문입니다.