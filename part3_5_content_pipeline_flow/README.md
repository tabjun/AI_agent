# CrewAI Content Pipeline Flow

이 프로젝트는 CrewAI의 Flow 기능을 활용하여 콘텐츠 생성 파이프라인을 구축하는 예제입니다.

## 🏗️ 아키텍처 다이어그램 (Architecture)

아래 다이어그램은 리서치부터 발행까지 이어지는 에이전트의 워크플로우를 보여줍니다.

![CrewAI Flow Architecture](./docs/crewai_flow_diagram.png)

---


graph TD
    Start([🚀 Start]) --&gt; Research[리서치]
    Research --&gt; Make[콘텐츠 작성]
    Make --&gt; Check[품질/SEO 검사]
    Check --&gt; Score{점수 &gt;= 8?}
    
    Score -- &quot;No (재작업)&quot; --&gt; Make
    Score -- &quot;Yes (통과)&quot; --&gt; Final([✅ 배포])
    
    style Score fill:#ff9,stroke:#333,stroke-width:2px
    style Make fill:#bbf,stroke:#333