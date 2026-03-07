# Part 7: OpenAI Agents SDK (ChatGPT Clone)

## 🏗️ System Architecture

```mermaid
graph TD
    %% 스타일 정의
    classDef user fill:#333,stroke:#666,color:white;
    classDef ui fill:#003366,stroke:#00aaff,color:white,stroke-width:2.5px,rx:8,ry:8,font-weight:bold;
    classDef sdk fill:#1a1a1a,stroke:white,color:white,stroke-width:2px,rx:10,ry:10;
    classDef model fill:#333,stroke:#999,color:white,stroke-dasharray: 5 5;
    classDef toolsHeader fill:#262626,stroke:none,color:white,font-weight:bold;
    classDef builtin fill:#3a3a3a,stroke:#777,color:#ccc,rx:5,ry:5;
    classDef external fill:#2d1d4d,stroke:#a060ff,color:#ddd,stroke-width:2px,rx:5,ry:5;

    %% 노드 배치
    User(User):::user
    Streamlit[ChatGPT-like UI<br/>Streamlit Entry Point]:::ui
    SDK[[OpenAI Agents SDK]]:::sdk
    Model(Model<br/>gpt-4o, gpt-4o-mini):::model
    Tools[Toolsets / Integrations]:::toolsHeader

    %% 연결 관계 (화살표 겹침 완화를 위해 순서 조정)
    User -->|프롬프팅| Streamlit
    Streamlit -->|에이전트 구동| SDK
    SDK <--> Model
    SDK --> Tools

    %% 도구 그룹화 (direction LR 제거 및 타이틀 간소화로 텍스트 겹침 해결)
    subgraph BuiltinGroup [OpenAI Standard Tools]
        WS[Web Search<br/>Bing/Google]:::builtin
        CI[Code Interpreter]:::builtin
        FS[File Search]:::builtin
        CALC[Calculator]:::builtin
        PY[Python interpreter]:::builtin
    end

    subgraph ExternalGroup [External Tools / MCP]
        YF[Yahoo Finance]:::external
        CC[Currency Converter]:::external
    end

    Tools --> BuiltinGroup
    Tools --> ExternalGroup
```

### 🎯 강의 목표
OpenAI의 Agents SDK와 Streamlit을 사용하여 한층 더 강화된 버전의 ChatGPT를 구축합니다. 이 에이전트는 웹 검색, 코드 실행, 이미지 생성 같은 핵심 기능은 물론, MCP를 통해 Yahoo Finance 데이터 조회나 환율 변환 같은 여러 외부 도구를 동시에 활용하는 강력한 기능까지 포함합니다.