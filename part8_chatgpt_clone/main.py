import asyncio
import streamlit as st
from agents import Agent, Runner, SQLiteSession, WebSearchTool, FileSearchTool
import dotenv
dotenv.load_dotenv()
import base64
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
                   vector_store_ids=[VECTOR_STORE_ID],
                   max_num_results=5
               )]
    )

agent = st.session_state['agent']

if 'session' not in st.session_state:
    st.session_state['session'] = SQLiteSession('chat-history', 'chat-gpt-clone-memory.db')

session = st.session_state['session']


async def display_chat_history():
    messages = await session.get_items()
    for message in messages:
        # ✅ dict가 아니면 스킵
        if not isinstance(message, dict):
            continue

        if 'role' in message and 'content' in message:
            with st.chat_message(message['role']):
                if isinstance(message['content'], list):
                    for item in message['content']:
                        if not isinstance(item, dict):
                            continue
                        if item.get('type') == 'input_text':
                            st.markdown(item['text'])
                        elif item.get('type') == 'text':
                            st.markdown(item['text'])
                        elif item.get('type') == 'input_image':
                            st.image(item['image_url'])
                else:
                    st.markdown(message['content'].replace('$', '\\$'))

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


async def run_agent(user_input):
    with st.chat_message('assistant'):
        status_container = st.status('⏳ Processing...', expanded=False)
        text_placeholder = st.empty()
        full_response = ''

        try:
            # ✅ 변경: 텍스트만 문자열로 전달 (이미지는 이미 세션에 add_items로 저장됨)
            stream = Runner.run_streamed(
                agent,
                user_input,
                session=session
            )

            async for event in stream.stream_events():
                if event.type == 'raw_response_event':
                    update_status(status_container, event.data.type)
                    if event.data.type == 'response.output_text.delta':
                        delta = getattr(event.data, 'delta', None)
                        if delta:
                            full_response += delta
                            text_placeholder.markdown(full_response.replace('$', '\\$'))
        except Exception as e:
            st.error(f"Error during agent execution: {e}")
            st.info("💡 과거 대화 기록과의 충돌일 수 있습니다. 사이드바의 'reset memory' 버튼을 눌러보세요.")


# UI
st.title("ChatGPT Clone (Vision Supported)")

asyncio.run(display_chat_history())

# 사이드바
with st.sidebar:
    reset = st.button("Reset memory")
    if reset:
        asyncio.run(session.clear_session())
    
    # ✅ 추가: 채팅 로그를 JSON으로 표시
    st.divider()
    st.subheader("Raw History Logs")
    history = asyncio.run(session.get_items())
    if history:
        for i, msg in enumerate(reversed(history)):
            with st.expander(f"Log {len(history) - i}"):
                if isinstance(msg, dict):
                    st.json(msg)
                elif isinstance(msg, str):
                    try:
                        import json
                        st.json(json.loads(msg))
                    except Exception:
                        st.code(msg)
                else:
                    st.write(msg)

# 채팅 입력
prompt = st.chat_input(
    'Write a message for your assistant',
    accept_file=True,
    file_type=["jpg", "jpeg", "png", 'txt']
)

if prompt:
    chat_image = None

    for file in prompt.files:
        if file.type.startswith('text/'):
            with st.chat_message('assistant'):
                with st.status(label='⏳ Processing text file...', state='running') as status:
                    uploaded_openai_file = client.files.create(
                        file=(file.name, file.getvalue()),
                        purpose='assistants'
                    )
                    client.beta.vector_stores.files.create(
                        vector_store_id=VECTOR_STORE_ID,
                        file_id=uploaded_openai_file.id
                    )
                    status.update(label='✅ Text file added to vector store!', state='complete')

        elif file.type.startswith('image/'):
            # ✅ 변경: base64 인코딩 → data URI → 세션에 input_image 형식으로 저장
            with st.status('⏳ Uploading image...') as status:
                base64_data = base64.b64encode(file.getvalue()).decode('utf-8')
                data_uri = f"data:{file.type};base64,{base64_data}"
                asyncio.run(
                    session.add_items([
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_image",
                                    "detail": "auto",
                                    "image_url": data_uri,   # 문자열로 저장
                                }
                            ],
                        }
                    ])
                )
                status.update(label='✅ Image uploaded', state='complete')
            with st.chat_message('human'):
                st.image(data_uri)

    if prompt.text:
        with st.chat_message('user'):
            st.markdown(prompt.text)
        asyncio.run(run_agent(prompt.text))