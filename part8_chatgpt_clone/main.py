import asyncio
import streamlit as st
from agents import Agent, Runner, SQLiteSession
import dotenv
dotenv.load_dotenv()

if 'agent' not in st.session_state:
    st.session_state['agent'] = Agent(
        name='ChatGpt Clone',
        instructions = """
        You are a helpful assistant that can remember previous conversations and use that information to provide better responses. You can also use the following tools to help you answer questions:
        """
    )
    
# 조건문 안에 넣으면 agent가 session_state에 없을 때만 선언되고
# undefined가 되기 때문에 바깥에 선언하는 것
agent = st.session_state['agent']

# rerun할때마다 세션이 초기화되는 것을 방지하기 위해 세션 상태에 저장
if 'session' not in st.session_state:
    st.session_state['session'] = SQLiteSession('chat-history', 'chat-gpt-clone-memory.db')
    
session = st.session_state['session']


## 위는 로직, 아래는 UI
# 대화 기록 보여주는 부분
async def display_chat_history():
    messages = await session.get_items()
    for message in messages:
        # 모두 role 가지고 있음. user = human, assistant = ai
        # 사이드바에 저장된 메세지를 화면에 불러와서 보여주게 하기 위해
        # with 구문으로 role의 메세지 불러오게 설정
        # dictonary 형태라서 message['role']로 불러와야 함
        # role이 'assistant'인 경우 Streamlit은 자동으로 AI 아이콘을 보여줍니다.
        with st.chat_message(message['role']):
            if message['role'] == 'user':
                st.markdown(message['content'])
            else:
                # Assistant 메세지 처리 (openai-agents 저장 구조 대응)
                if 'content' in message:
                    if isinstance(message['content'], list) and len(message['content']) > 0:
                        content_text = message['content'][0].get('text', '')
                        st.markdown(content_text)
                    elif isinstance(message['content'], str):
                        st.markdown(message['content'])

# 메세지 출력을 prompt 입력보다 먼저 실행하여 대화 흐름 유지
asyncio.run(display_chat_history())

# assistant 응답 부분 꾸미기
async def run_agent(user_prompt):
    with st.chat_message('ai'):
        text_placeholder = st.empty()
        full_response = ''

        stream = Runner.run_streamed(
            agent,
            user_prompt,
            session=session
        )

        async for event in stream.stream_events():
            if event.type == 'raw_response_event':
                if event.data.type == 'response.output_text.delta':
                    # 속성 이름을 delta로 확인 (또는 text가 맞는지 확인 필요)
                    # 안전하게 hasattr 또는 getattr 사용 가능
                    delta = getattr(event.data, 'delta', None)
                    if delta:
                        full_response += delta
                        text_placeholder.markdown(full_response)


prompt = st.chat_input('Write a message for your assistant')

if prompt:
    # 사용자 메세지 즉시 표시
    with st.chat_message('human'):
        st.markdown(prompt)

    # AI 응답 생성 및 표시
    asyncio.run(run_agent(prompt))

        
# 여기서 중요한건 if prompt 구문에서 run_agent를 사용하지만, st.chat_message('ai'): 구문과 함께
# run_agent 함수는 ai로 chat_message를 생성하는데, st.chat_message('ai'): 구문에 적용 불가함.
# chat_message('human')안에 chat_message('ai') 생성 불가
# 그래서 asyncio.run(run_agent(prompt)) 코드를 if 구문 밖에 넣어야 함


# 사이드바가 밑에 있어야, prompt가 입력되고 나서 사이드바가 보여짐
with st.sidebar:
    reset = st.button('reset memory')
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))