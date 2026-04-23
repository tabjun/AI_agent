import asyncio
import streamlit as st
from agents import Agent, Runner, SQLiteSession, WebSearchTool, FileSearchTool
import time
import dotenv
dotenv.load_dotenv()
import base64
from io import BytesIO
from openai import OpenAI

client = OpenAI()

VECTOR_STORE_ID = 'vs_69ea1ac59b5c8191a0d32df71038261e'


# 에이전트 초기화
if 'agent' not in st.session_state:
    st.session_state['agent'] = Agent(
        name='ChatGpt Clone',
        instructions="""
        You are a helpful assistant that can process both text, images, and documents.
        1. When an image is provided, analyze it carefully.
        2. When a user asks about their own information, files, or documents, YOU MUST USE the 'File Search Tool' to find the answer in the connected vector store.
        3. For current events or general knowledge, use 'Web Search Tool'.
        Always check the files first if the user mentions something that sounds like it's in their personal records.
        """,
        tools=[WebSearchTool(),
               FileSearchTool(
                   vector_store_ids = [
                       VECTOR_STORE_ID
                   ],
                   max_num_results=5
               )]
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
                    st.markdown(message['content'].replace('$','\\$'))
        
        if 'type' in message:
            if message['type'] == 'web_search_call':
                with st.chat_message('assistant'):
                    st.markdown('🔎 searched the web.....')
            elif message['type'] == 'file_search_call':
                with st.chat_message('assistant'):
                    st.markdown('📄 searched the files.....')

def update_status(status_container, event):
    status_messages = {
        'response.web_search_call.completed': ('✅ Web search complete!', 'complete'),
        'response.web_search_call.in_progress': ('⏳ Starting web search...', 'running'),
        'response.web_search_call.searching': ('🔍 Searching the web...', 'running'),
        'response.file_search_call.completed': ('✅ File search complete!', 'complete'),
        'response.file_search_call.in_progress': ('📄 Starting file search...', 'running'),
        'response.file_search_call.searching': ('📄 Searching files...', 'running'),
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
        
        # 멀티모달 입력 구성: 텍스트만 있을 때와 이미지가 있을 때를 명확히 구분
        if image_file:
            b64_image = img_to_base64(image_file)
            content = [
                {"type": "text", "text": user_input},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
            ]
        else:
            # Agents SDK 400 에러 방지를 위해 텍스트만 있을 때는 문자열로 전달
            content = user_input

        try:
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
                            text_placeholder.markdown(full_response.replace('$','\\$'))
        except Exception as e:
            st.error(f"Error during agent execution: {e}")
            st.info("💡 과거 대화 기록과의 충돌일 수 있습니다. 사이드바의 'reset memory' 버튼을 눌러보세요.")

# UI 구성
st.title("ChatGPT Clone (Vision Supported)")

# 대화 기록 표시
asyncio.run(display_chat_history())

# --- 사이드바 구성 ---
with st.sidebar:
    st.header("Settings & Tools")
    # 이미지 업로더
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image Preview", use_container_width=True)
    
    st.divider()
    # 메모리 리셋 버튼 (확실하게 배치)
    if st.button('Reset Memory'):
        asyncio.run(session.clear_session())
        st.rerun()

# --- 채팅 입력 및 처리 ---
prompt = st.chat_input('Write a message for your assistant',
                       accept_file=True,
                       file_type = ["jpg", "jpeg", "png", 'txt'])

if prompt:
    chat_image = None
    # 파일 처리 루프
    for file in prompt.files:
        if file.type.startswith('text/'):
            with st.chat_message('assistant'):
                with st.status(label='⏳ Processing text file...', state='running') as status:
                    uploaded_openai_file = client.files.create(
                        file=(file.name, file.getvalue()),
                        purpose = 'assistants'
                    )    
                    client.beta.vector_stores.files.create(
                        vector_store_id = VECTOR_STORE_ID,
                        file_id = uploaded_openai_file.id
                    )
                    status.update(label='✅ Text file added to vector store!', state='complete')
        elif file.type.startswith('image/'):
            chat_image = file
        
    if prompt.text:
        with st.chat_message('user'):
            st.markdown(prompt.text)
        
        # 이미지 우선순위 결정
        image_to_use = uploaded_file if uploaded_file else chat_image
        asyncio.run(run_agent(prompt.text, image_file=image_to_use))
