# 2026.4.22 학습 내용 에이전트 구현(function tool 활용해서 다른 도구를 가져오는 것이 아닌 openaiagentsdk + openai모델 페어해서 슬때 사용가능한 내장 함수: hosted tools 활용)

### 1. 핵심 개념: Hosted Tools (내장 도구)
기존의 `function calling`은 개발자가 직접 함수를 정의하고 실행 로직을 작성해야 했습니다. 반면, **OpenAI Agent SDK의 Hosted Tools**는 OpenAI 인프라에서 직접 실행되는 도구(예: `websearchtool`)를 모델에 간단히 연결만 하면 바로 사용 가능한 방식입니다.

### 2. 전체 코드 Flow
1.  **사용자 입력:** `st.chat_input`을 통해 질문이 들어옴.
2.  **에이전트 실행:** `Runner.run_streamed(agent, user_prompt, session=session)` 호출.
3.  **도구 판단:** 모델이 "이건 검색이 필요해"라고 판단하면 내부적으로 `websearchtool`을 실행.
4.  **중간 데이터 발생 (중요):** 
    - 웹 검색을 하겠다는 의도(`tool_calls`) 메시지 발생.
    - 검색 결과 데이터(`tool_outputs`) 메시지 발생.
5.  **세션 저장:** `SQLiteSession`은 대화의 맥락을 유지하기 위해 위 4번의 **모든 중간 과정 메시지를 DB에 기록**.
6.  **UI 렌더링:** `display_chat_history()`가 DB의 모든 데이터를 읽어와서 `st.chat_message()`로 화면에 그리려 시도.

### 3. 'role' Key Error가 발생하는 이유
`websearchtool`을 사용하면 세션(DB)에 일반적인 텍스트 메시지 외에 다음과 같은 데이터가 섞여 들어갑니다.

*   **일반 메시지:** `{"role": "user", "content": "오늘 날씨 어때?"}` -> **성공**
*   **도구 관련 데이터:** `{"tool_call_id": "...", "type": "function", ...}` (role 키가 없음) -> **KeyError: 'role' 발생!**

즉, `websearchtool`이 동작하면서 생성하는 **내부 관리용 메시지나 도구 실행 결과값들이 `role`이라는 키를 가지고 있지 않은 형태**로 DB에 저장되기 때문에, 이를 무조건 UI로 출력하려 할 때 에러가 발생하게 됩니다.

### 4. 해결 방법: 방어적 코드 추가
```python
if 'role' in message and 'content' in message:
    # 이 조건문은 "UI에 출력할 수 있는 표준 규격의 메시지만 처리하겠다"는 뜻입니다.
    with st.chat_message(message['role']):
        ...
```
이 코드를 추가함으로써, `role`이 없는 도구 실행 데이터는 UI 출력 대상에서 제외(무시)하고, 실제 사용자나 AI의 완성된 답변(텍스트 메시지)만 화면에 보여주게 되어 에러 없이 안정적으로 실행됩니다.

---

# 2026.4.22 학습 내용: 비동기(Asyncio)와 코드 실행 흐름 이해

### 1. 비동기(Asynchronous) 처리를 사용하는 이유
본 프로젝트에서 `asyncio`를 사용하는 이유는 크게 두 가지입니다.
- **I/O Bound 작업 효율화:** 데이터베이스(SQLite) 접근이나 OpenAI API 호출은 응답을 기다려야 하는 작업입니다. 비동기 처리를 통해 기다리는 시간 동안 프로그램이 멈추지(Blocking) 않게 합니다.
- **SDK 요구사항:** `openai-agent-sdk`는 비동기 방식으로 설계된 라이브러리입니다. 에이전트의 실행(`Runner`)과 세션 관리(`SQLiteSession`)가 모두 비동기 함수로 구현되어 있어 이를 호출하기 위해 `asyncio.run()` 또는 `await`가 필수적입니다.

### 2. 비동기 vs 동기 비유
- **동기(Sync):** 요리가 나올 때까지 카운터 앞에 줄 서서 기다리기 (프로그램 멈춤)
- **비동기(Async):** 주문 후 진동벨을 받고 자리에 앉아 있기. 요리가 되는 동안 휴대폰을 보거나 다른 일을 할 수 있음 (프로그램이 대기 시간에도 다른 작업 수행 가능)

### 3. 코드 실행 순서 (`display_chat_history`)
```python
# 1. 함수 정의 (설계도)
async def display_chat_history(): ... 

# 2. 실제 실행 (과거 기록 불러오기)
asyncio.run(display_chat_history()) 

# 3. 입력창 표시
prompt = st.chat_input(...) 
```
- **순서의 중요성:** `st.chat_input`보다 위에 실행 코드를 배치하여, 사용자가 새 메시지를 입력하기 전 과거 대화가 화면에 먼저 렌더링되도록 구현했습니다. 이를 통해 끊김 없는 대화 흐름(Chat UX)을 유지합니다.
