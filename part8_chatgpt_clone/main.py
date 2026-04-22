import asyncio
import streamlit as st
from agents import Agent, Runner, SQLiteSession, WebSearchTool
import time
import dotenv
import base64
from io import BytesIO

dotenv.load_dotenv()

# 에이전트 초기화
if 'agent' not in st.session_state:
    st.session_state['agent'] = Agent(
        name='ChatGpt Clone',
        instructions="""
        You are a helpful assistant that can process both text and images.
        When an image is provided, analyze it carefully and answer user's questions about it.
        You can also use the following tools:
        1. Web Search Tool: Use this for information outside your training data.
        """,
        tools=[WebSearchTool()]
    )

agent = st.session_state['agent']

# 세션 초기화
if 'session' not in st.session_state:
    st.session_state['session'] = SQLiteSession('chat-history', 'chat-gpt-clone-memory.db')

session = st.session_state['session']

def img_to_base64(image_file):
    return base64.b64encode(image_file.getvalue()).decode()

async def display_chat_history():
    messages = await session.get_items()
    for message in messages:
        if 'role' in message and 'content' in message:
            with st.chat_message(message['role']):
                if isinstance(message['content'], list):
                    for item in message['content']:
                        if 'text' in item:
                            st.markdown(item['text'])
                        if 'image_url' in item:
                            st.image(item['image_url']['url'])
                else:
                    st.markdown(message['content'])
        
        if 'type' in message and message['type'] == 'web_search_call':
            with st.chat_message('assistant'):
                st.markdown('🔎 searched the web.....')

def update_status(status_container, event):
    status_messages = {
        'response.web_search_call.completed': ('✅ Web search complete!', 'complete'),
        'response.web_search_call.in_progress': ('⏳ Starting web search...', 'running'),
        'response.web_search_call.searching': ('🔍 Searching the web...', 'running'),
        'response.completed': ('✅ Done', 'complete'),
    }
    if event in status_messages:
        label, state = status_messages[event]
        status_container.update(label=label, state=state)

async def run_agent(user_input, image_file=None):
    with st.chat_message('assistant'):
        status_container = st.status('⏳ Processing...', expanded=False)
        text_placeholder = st.empty()
        full_response = ''
        
        # 멀티모달 입력 구성
        content = [{"type": "text", "text": user_input}]
        if image_file:
            b64_image = img_to_base64(image_file)
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}
            })

        stream = Runner.run_streamed(
            agent,
            content,
            session=session
        )

        async for event in stream.stream_events():
            if event.type == 'raw_response_event':
                update_status(status_container, event.data.type)
                if event.data.type == 'response.output_text.delta':
                    delta = getattr(event.data, 'delta', None)
                    if delta:
                        full_response += delta
                        text_placeholder.markdown(full_response)

# UI 구성
st.title("ChatGPT Clone (Vision Supported)")

# 대화 기록 표시
asyncio.run(display_chat_history())

# 이미지 업로더 추가
uploaded_file = st.sidebar.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    st.sidebar.image(uploaded_file, caption="Uploaded Image Preview", use_container_width=True)

prompt = st.chat_input('Write a message for your assistant')

if prompt:
    with st.chat_message('user'):
        st.markdown(prompt)
        if uploaded_file:
            st.image(uploaded_file, width=300)

    asyncio.run(run_agent(prompt, uploaded_file))

with st.sidebar:
    st.divider()
    if st.button('reset memory'):
        asyncio.run(session.clear_session())
        st.rerun()
