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

## 🤖 Dummy Agent: Runner를 쓰는 이유

Dummy agent를 만들 때 `Runner`를 사용하는 핵심 이유는, 단순히 "모델 1회 호출"이 아니라 **에이전트 실행 루프 전체를 표준 방식으로 관리**해주기 때문입니다.

`Runner`는 내부적으로 아래와 같은 반복 루프를 수행합니다.

1. Agent + Input으로 모델에 요청
2. 모델 응답 파싱
3. Tool 호출 필요 여부 판단
4. 필요하면 Tool 실행 후 결과를 다시 모델에 전달
5. 최종 응답이 나오면 종료하고 사용자에게 반환

즉, 우리가 적어둔 설명처럼 `while true`에 가까운 오케스트레이션을 `Runner`가 책임집니다.

### Runner 실행 구조도 (Flow)

```mermaid
flowchart TD
    A["시작: Runner.run(agent, user_input)"] --> B["대화 컨텍스트 구성<br/>(agent instructions + history + input)"]
    B --> C["OpenAI 모델 호출"]
    C --> D["모델 응답 파싱"]
    D --> E{"Tool 호출 필요?"}
    E -- 예 --> F["해당 Tool 실행"]
    F --> G["Tool 결과를 대화 컨텍스트에 추가"]
    G --> C
    E -- 아니오 --> H["최종 응답(final response) 확정"]
    H --> I["Runner가 결과 반환"]
```

### Runner 실행 시퀀스 (Sequence)

```mermaid
sequenceDiagram
    participant U as User
    participant R as Runner
    participant M as OpenAI Model
    participant T as Tool(선택)

    U->>R: 질문 입력
    R->>M: agent + instructions + input 전달
    M-->>R: 응답(텍스트 또는 tool call)

    alt tool call 포함
        R->>T: tool 실행 요청
        T-->>R: tool 실행 결과
        R->>M: tool 결과 포함해 재요청
        M-->>R: 최종 답변
    else tool call 없음
        M-->>R: 최종 답변
    end

    R-->>U: 최종 응답 출력
```

### 단계별 상세 설명

1. 입력 수집
사용자 입력과 Agent 설정(`name`, `instructions`, `tools`)을 Runner가 묶어서 실행 단위를 만듭니다.

2. 모델 호출
Runner는 OpenAI 모델에 요청을 보내고, 일반 텍스트 응답인지 tool call 응답인지 확인할 준비를 합니다.

3. 응답 파싱
모델 출력에서 구조화된 신호(예: tool 호출 의도, 인자)를 읽어 다음 액션을 결정합니다.

4. Tool 실행 분기
Tool 호출이 필요하면 Runner가 직접 해당 함수를 실행합니다. 이때 필요한 인자를 전달하고 실행 결과를 수집합니다.

5. 재호출 루프
Tool 결과를 다시 모델에 전달하여 후속 추론을 진행합니다. Tool이 연쇄적으로 필요하면 이 과정을 반복합니다.

6. 종료 조건
더 이상 tool call이 없고 사용자에게 보여줄 최종 텍스트가 생성되면 루프를 종료하고 결과를 반환합니다.

### Dummy Agent 코드와 연결해서 보기

`dummy_agent.ipynb`에 있는 아래 호출이 위 전체 루프를 실행합니다.

```python
result = await Runner.run(agent, "Hello how are you?")
```

이 한 줄이 하는 일은 "모델 한 번 호출"이 아니라,
**모델 호출 → 파싱 → tool 실행(필요 시) → 재호출 → 최종 응답 반환**까지의 전 과정을 담당하는 것입니다.

### 학습 포인트 정리

- `Agent`는 역할/규칙/도구 정의
- `Runner`는 실행 오케스트레이션(루프, 분기, 종료)
- 도구가 많아질수록 `Runner`의 가치가 커짐
- 실무에서는 직접 루프를 구현하기보다 `Runner`로 표준화하는 것이 안정적

## 📘 2026.04.01(수) 강의 마무리 노트

2026.04.01(수)은 OpenAI Agents SDK의 가장 기초이자 핵심인 **Agent + Runner + Tool 연결 흐름**을 학습했습니다.

dummy agent 코드는 "에이전트를 정의하고 호출하면 내부에서 어떤 일이 일어나는지"를 눈으로 확인하기 위한 최소 예제입니다.

### 2026.04.01(수) 실습 코드의 의미

```python
from agents import Agent, Runner, function_tool

@function_tool
def get_weather(city: str):
    """get weather by city"""
    print(city)
    return "30 degrees"

agent = Agent(
    name="Assistant Agent",
    instructions="You are a helpful assistant. Use tools when needed to answer questions",
    tools=[get_weather],
)

stream = Runner.run_streamed(
    agent,
    "Hello how are you? what is the weather in the capital of korea",
)
```

핵심은 `Runner.run_streamed(...)`를 호출하는 순간부터,
에이전트 실행 루프(모델 요청 → 응답 파싱 → tool 호출 판단 → tool 실행 → 재요청 → 최종 응답)가 자동으로 진행된다는 점입니다.

### stream 이벤트에서 본 결과 타입 해설

`async for event in stream.stream_events()`에서 관찰한 항목은 다음 의미를 가집니다.

- `tool_call_item`: 에이전트가 "이 문제를 풀기 위해 tool이 필요하다"고 판단해 tool 호출을 생성한 단계
- `tool_call_output_item`: 실제 tool 함수가 실행되고 결과값이 반환된 단계
- `message_output_item`: tool 결과까지 반영해 에이전트가 사용자에게 최종 메시지를 생성한 단계

즉, 적어둔 주석 설명은 단순 추측이 아니라, 스트리밍 이벤트 로그로 검증된 실행 순서입니다.

### 2026.04.01(수) 학습 한 줄 정리

"Agent를 호출해서 사용한다"는 말의 실제 의미는,
**Runner가 에이전트 실행 전 과정을 반복 오케스트레이션하면서 최종 답을 완성해 주는 흐름**이라는 것입니다.

## 2026.04.14 학습 내용: 에이전트 Handoff 라우팅 흐름 변화 및 출력 제어 (output_type)

최근 OpenAI Agents SDK의 업데이트에 따라 다중 에이전트(Multi-Agent) 간의 제어권 전환(Handoff) 흐름이 변경되었습니다. 이에 맞춰 Pydantic 기반의 구조화된 응답(Answer 타입 등)을 얻기 위한 `output_type` 파라미터의 선언 위치도 명확히 조정해야 합니다.

### 1. 변경된 Handoff 실행 흐름
과거에는 서브 에이전트로 제어권이 넘어가면 해당 에이전트가 바로 사용자에게 최종 응답을 반환할 수 있었습니다. 하지만 현재 SDK 구조에서는 서브 에이전트의 작업 결과가 반드시 다시 메인 에이전트로 회귀하여 최종 래핑(Wrapping)을 거친 후 출력됩니다.

[작동 흐름도]
1. Main Agent가 사용자 요청 수신 및 의도 분석
2. 적합한 서브 에이전트(예: Weather Agent)로 제어권 전환(Handoff)
3. 서브 에이전트가 Task 수행 및 결과 생성
4. 생성된 결과를 다시 Main Agent로 반환 (핵심 변경점)
5. Main Agent가 최종 텍스트 또는 구조화된 객체로 래핑하여 사용자에게 반환

### 2. output_type 적용 위치 수정
위와 같은 사이클 변화로 인해, 최종적으로 사용자에게 결괏값을 리턴하는 주체는 서브 에이전트가 아닌 **Main Agent**가 되었습니다. 

따라서 지정한 `Answer` 모델 타입대로 출력이 나오지 않는다면, 각각의 개별 전문가 에이전트가 아니라 관문 역할을 하는 `main_agent` 내부에 `output_type=Answer`를 할당해야만 의도한 포맷의 결과물을 얻을 수 있습니다.

[코드 적용 예시]
```python
from agents import Agent

# Answer 클래스가 Pydantic BaseModel로 사전 정의되어 있다고 가정

main_agent = Agent(
    name="Main Agent",
    instructions="You are a user facing agent. Transfer to the agent most capable of answering the user's question.",
    handoffs=[geography_agent, economics_agent], # 라우팅 대상 서브 에이전트 목록 전달
    output_type=Answer, # 최종 결과를 래핑하여 리턴하는 주체가 Main Agent이므로 여기에 타입 명시
)

## 2026.04.14 학습 내용: draw_graph를 활용한 에이전트 흐름도 시각화

`agents.extensions.visualization`에서 제공하는 `draw_graph` 함수를 통해, 에이전트 구조(handoff 연결 및 tool 호출 관계)를 그래프 이미지로 시각화할 수 있습니다.

### 1. draw_graph 사용법

```python
from agents.extensions.visualization import draw_graph

draw_graph(main_agent)
```

`main_agent`를 기준으로 연결된 handoff 에이전트와 tool들을 자동으로 순회하며 방향 그래프를 생성합니다.  
Jupyter 환경에서는 인라인 이미지로 바로 출력되므로 복잡한 멀티 에이전트 구조를 빠르게 파악하는 데 유용합니다.

### 2. 환경 설정

`draw_graph`는 내부적으로 Graphviz를 의존합니다. 두 가지 설치가 모두 필요합니다.

**Python 패키지 설치 (uv 사용)**
```bash
uv add graphviz
```

**시스템 Graphviz 설치 (Windows 기준)**  
[https://graphviz.org/download/](https://graphviz.org/download/) 에서 설치 후, 설치 경로를 시스템 환경변수 `PATH`에 추가해야 합니다.  
(예: `C:\Program Files\Graphviz\bin`)

> Python 패키지만 설치하고 시스템 Graphviz가 없으면 실행 시 오류가 발생합니다.

### 3. Pydantic output_type과 draw_graph의 조합

draw_graph로 구조를 시각적으로 먼저 파악한 다음, 최종 응답이 흘러나오는 경로를 보면  
**마지막에 결과를 내보내는 에이전트가 어디인지** 확인할 수 있습니다.

최신 SDK 흐름에서 서브 에이전트는 결과를 Main Agent에게 돌려주므로, `output_type`은 반드시 **Main Agent**에 선언해야 합니다.

```
Main Agent
    ↓ handoff
Weather Agent (작업 수행)
    ↓ 결과 반환
Main Agent (최종 래핑 → output_type 적용)
    ↓
사용자에게 Answer 타입으로 반환
```

draw_graph를 통해 이 흐름을 눈으로 확인하고, `output_type` 선언 위치가 적절한지 검증하는 조합이 효과적입니다.

--# 2026.04.19 학습 내용: Streamlit API 활용 UI 생성 실습
---

## 🖥️ UI Preview

### 1. 실시간 실행 화면 (GitHub Pages)
아래 링크를 통해 별도의 설치 없이 브라우저에서 UI를 바로 확인할 수 있습니다.
- **[실시간 UI 확인하기 (GitHub Pages 클릭)](#)** 
*(주의: 레포지토리 Settings에서 Pages 설정을 완료해야 링크가 활성화됩니다.)*

### 2. UI Screenshot
캡처한 이미지는 아래에서 확인할 수 있습니다.

![UI Screenshot](./example_image/ui_example.png)

---
## 🚀 GitHub Pages 설정 방법 (필수)
1. GitHub 레포지토리 페이지로 이동합니다.
2. **Settings** 메뉴를 클릭합니다.
3. 왼쪽 사이드바에서 **Pages**를 선택합니다.
4. **Build and deployment > Branch** 섹션에서:
   - Branch를 `main`으로 선택
   - 폴더를 `/(root)`가 아닌 `/docs`로 변경합니다.
5. **Save** 버튼을 누르고 약 1~2분 뒤 상단에 표시되는 URL로 접속합니다.
