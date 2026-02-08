# CrewAI Content Pipeline Flow

이 프로젝트는 CrewAI의 Flow 기능을 활용하여 콘텐츠 생성 파이프라인을 구축하는 예제입니다.

## 🏗️ 아키텍처 다이어그램 (Architecture)

아래 다이어그램은 리서치부터 발행까지 이어지는 에이전트의 워크플로우를 보여줍니다.

![CrewAI Flow Architecture](./docs/crewai_flow_diagram.png)

---


## 🏗️ Detailed Flow Architecture

```mermaid
graph TD
    %% 노드 정의: 따옴표를 사용하여 공백 문제를 방지합니다.
    Start([Start])
    Init["초기 설정 및 검증"]
    Research["리서치 수행"]
    TypeRouter{"콘텐츠 타입 결정"}

    MakeBlog["블로그 작성 및 수정"]
    MakeTweet["트윗 작성 및 수정"]
    MakeLinkedIn["링크드인 작성 및 수정"]

    CheckSEO["SEO 품질 검사"]
    CheckViral["화제성 검사"]

    ScoreRouter{"점수 8점 이상?"}
    Final([Final Content])

    %% 흐름 연결
    Start --> Init
    Init --> Research
    Research --> TypeRouter

    %% 분기 경로
    TypeRouter -- "Blog" --> MakeBlog
    TypeRouter -- "Tweet" --> MakeTweet
    TypeRouter -- "LinkedIn" --> MakeLinkedIn

    %% 검수 단계
    MakeBlog --> CheckSEO
    MakeTweet --> CheckViral
    MakeLinkedIn --> CheckViral

    %% 품질 평가 및 루프 (Refinement Loop)
    CheckSEO --> ScoreRouter
    CheckViral --> ScoreRouter

    %% 재작업 경로 (Loop)
    ScoreRouter -- "No (재작업)" -.-> MakeBlog
    ScoreRouter -- "No (재작업)" -.-> MakeTweet
    ScoreRouter -- "No (재작업)" -.-> MakeLinkedIn

    %% 최종 통과
    ScoreRouter -- "Yes (통과)" --> Final
```