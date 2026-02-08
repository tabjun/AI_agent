# CrewAI Content Pipeline Flow

이 프로젝트는 CrewAI의 Flow 기능을 활용하여 콘텐츠 생성 파이프라인을 구축하는 예제입니다.

## 🏗️ 아키텍처 다이어그램 (Architecture)

아래 다이어그램은 리서치부터 발행까지 이어지는 에이전트의 워크플로우를 보여줍니다.

![CrewAI Flow Architecture](./docs/crewai_flow_diagram.png)

---


## 🏗️ Detailed Flow Architecture

```mermaid
graph TD
    %% 노드 정의
    Start([Start Flow])
    Init[초기 설정 및 검증]
    Research[리서치 수행]
    
    %% 분기 결정 (Router)
    TypeRouter{콘텐츠 타입 결정}
    
    %% 작업 노드
    MakeBlog[블로그 작성 및 수정]
    MakeTweet[트윗 작성 및 수정]
    MakeLinkedIn[링크드인 작성 및 수정]
    
    %% 검수 노드
    CheckSEO[SEO 품질 검사]
    CheckViral[화제성 검사]
    
    %% 품질 평가 (Score Router)
    ScoreCheck{점수 8점 이상?}
    Final([최종 완성])

    %% 흐름 연결
    Start --> Init
    Init --> Research
    Research --> TypeRouter

    %% 분기 경로
    TypeRouter --> MakeBlog
    TypeRouter --> MakeTweet
    TypeRouter --> MakeLinkedIn

    %% 검수 단계
    MakeBlog --> CheckSEO
    MakeTweet --> CheckViral
    MakeLinkedIn --> CheckViral

    %% 루프 로직 (Refinement Loop)
    CheckSEO --> ScoreCheck
    CheckViral --> ScoreCheck

    %% 재작업 경로 (Loop)
    ScoreCheck -- "재작업" --> MakeBlog
    ScoreCheck -- "재작업" --> MakeTweet
    ScoreCheck -- "재작업" --> MakeLinkedIn

    %% 최종 통과
    ScoreCheck -- "통과" --> Final
```