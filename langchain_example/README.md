# LangChain vs. LangGraph 개별 구현 가이드

이 폴더는 두 프레임워크의 차이를 코드 레벨에서 명확히 비교하기 위해 각각 개별적인 파일로 구현되었습니다.

---

## 1. 개별 구현 파일 정보

### 📗 LangChain 단순 에이전트 (`langchain_agent.py`)
- **특징**: `AgentExecutor`를 사용하는 표준 방식입니다.
- **구조**: `Prompt -> Agent -> Tool -> Output`으로 이어지는 선형적인 흐름입니다.
- **장점**: 설정이 매우 빠르고 코드가 간결합니다.

### 📘 LangGraph 상태 에이전트 (`langgraph_agent.py`)
- **특징**: 그래프와 노드(Node)를 직접 설계하는 방식입니다.
- **구조**: `State(기억)`를 중심으로 루프(Cycle)와 복잡한 분기 처리가 가능합니다.
- **장점**: 에이전트의 사고 과정을 단계별로 통제할 수 있습니다.

---

## 2. 기존 에이전트 응용 (Advanced)
엔진과 역할을 분리하여 더 고도화한 사례입니다.
- `main.py`: 기술 연구 전문가 에이전트 (LangGraph 기반)
- `job_hunter.py`: 채용 컨설팅 전문가 에이전트 (LangGraph 기반)

---

## 3. 실행 방법 (uv run)
```bash
# LangChain 실행
uv run langchain_agent.py

# LangGraph 실행
uv run langgraph_agent.py
```
