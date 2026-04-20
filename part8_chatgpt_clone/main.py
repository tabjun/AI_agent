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
async def run_agent(message):
    stream = Runner.run_streamed(
        agent,
        message,
        session=session
    )

    async for event in stream.stream_events():
        if event.type == 'raw_response_event':
            if event.data.type == 'response.output_text.delta':
                with st.chat_message('ai'):
                    st.write(event.data.delta)
    
    
   
prompt = st.chat_input('Write a message for your assistant')

if prompt:
    with st.chat_message('human'):
        st.write(prompt)
        # 비동기 함수라서 asyncio로 감싸줘야 함
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