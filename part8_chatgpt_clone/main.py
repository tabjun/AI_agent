import asyncio
import streamlit as st
from agents import (
    Agent,
    Runner,
    SQLiteSession,
    WebSearchTool,
    FileSearchTool,
    ImageGenerationTool,
    CodeInterpreterTool,
)
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
        4. Code Interpreter Tool: Use this tool when you need to write and run code to answer the user's question. 
        """,
        tools=[WebSearchTool(),
               FileSearchTool(
                   vector_store_ids=[VECTOR_STORE_ID],
                   max_num_results=5
               ),
               ImageGenerationTool(
                   tool_config={
                       'type': 'image_generation',
                       'quality': 'auto',
                       'output_format': 'jpeg',
                       'moderation': 'low',
                       # 이미지 그려지면서 중간에 보여주는거
                       'partial_images': 1
                    },
               ),
               CodeInterpreterTool(
                   tool_config={
                       'type': 'code_interpreter',
                       'container': {
                           'type' : 'auto',
                       },
                   }
               )
               ]
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
                            st.markdown(item.get('text', ''))
                        elif item.get('type') in ('text', 'output_text'):
                            st.markdown(item.get('text', ''))
                        elif item.get('type') == 'input_image':
                            st.image(item['image_url'])
                else:
                    st.markdown(message['content'].replace('$', '\\$'))

        if 'type' in message:
            # 생성한 이미지, 새로고침 후에도 저장돼서 계속 노출되게
            message_type = message['type']
            if message_type == 'web_search_call':
                with st.chat_message('assistant'):
                    st.markdown('🔎 searched the web.....')
            elif message_type == 'file_search_call':
                with st.chat_message('assistant'):
                    st.markdown('📄 searched the files.....')
            elif message_type == 'image_generation_call':
                # 이미지 생성 후 로그보면 result에 base64로 인코딩된 이미지 데이터가 저장되어 있음. 이걸 디코딩해서 보여주기
                image = base64.b64decode(message['result'])
                with st.chat_message('assistant'):
                    st.image(image)
                    st.markdown('🎨 generated an image.....')
            elif message_type == 'code_interpreter_call':
                # 실제 저장 키는 사이드바 로그에서 확인 필요
                code = message.get('code') or message.get('result', '')
                with st.chat_message('assistant'):
                    if code:
                        st.code(code)
                    st.markdown('💻 wrote some code.....')


def update_status(status_container, event):
    status_messages = {
        # web_search status
        'response.web_search_call.in_progress': ('🔍 Starting web search...', 'running'),
        'response.web_search_call.searching':   ('🔍 Searching the web...', 'running'),
        'response.web_search_call.completed':   ('✅ Web search complete!', 'complete'),
        
        # file_search status
        'response.file_search_call.in_progress': ('📂 Starting file search...', 'running'),
        'response.file_search_call.searching':   ('📂 Searching files...', 'running'),
        'response.file_search_call.completed':   ('✅ File search complete!', 'complete'),
        
        # image generation status
        'response.image_generation_call.in_progress': ('🎨 Preparing...', 'running'),
        'response.image_generation_call.generating':  ('🖼️ Generating image...', 'running'),
        'response.image_generation_call.completed':   ('✅ Image generated!', 'complete'),
        
        # code interpreter status
        'response.code_interpreter_call.in_progress':  ('💻 Writing code...', 'running'),
        'response.code_interpreter_call.interpreting': ('⚙️ Interpreting...', 'running'),
        'response.code_interpreter_call.code.done':    ('⚙️ Executing...', 'running'),
        'response.code_interpreter_call.completed':    ('✅ Code execution complete!', 'complete'),

        # 전체 완료
        'response.completed': ('✅ Done', 'complete'),
    }
    if event in status_messages:
        label, state = status_messages[event]
        status_container.update(label=label, state=state)


async def run_agent(user_input):
    with st.chat_message('assistant'):
        status_container = st.status('⏳ Processing...', expanded=False)
        # 이전 코드에는 text_placeholder가 위에 있었는데, 그러면 streamlit 코드 구현 방식에 의해 이미지나 코드가 생성되고, 다시 제일 첫줄에 
        # 프롬프트 답변이 생성됨. 원하는 결과는 생성 요청한 이미지나 코드가 쭉 나온 후 마지막에 텍스트 답변이 나와야 하기 때문에 순서 변경
        image_placeholder = st.empty()
        code_placeholder = st.empty()
        text_placeholder = st.empty()
        full_response = ''
        code_response = ''

        # image_placeholder.empty(), text_placeholder.empty(), code_placeholder.empty() 이거 3개만 쓰면, 새로고침 후 이전 답변 무조건 비워짐
        # 사용자가 새로운 메세지 보낼 때만 컨테이너 비워지게 설정 필요
        # 완성된 컨테이너를  st.session에 캐싱하게 수정
        st.session_state['code_placeholder'] = code_placeholder
        st.session_state['image_placeholder'] = image_placeholder
        st.session_state['text_placeholder'] = text_placeholder
        
        try:
            # ✅ 변경: 텍스트만 문자열로 전달 (이미지는 이미 세션에 add_items로 저장됨)
            stream = Runner.run_streamed(
                agent,
                user_input,
                session=session
            )
            # imagegeneration 툴 중 async for(130번째 라인, 강의 코드) 부분
            async for event in stream.stream_events():
                if event.type == 'raw_response_event':
                    update_status(status_container, event.data.type)
                    if event.data.type == 'response.output_text.delta':
                        delta = getattr(event.data, 'delta', None)
                        if delta:
                            full_response += delta
                            text_placeholder.markdown(full_response.replace('$', '\\$'))
                    
                    # code interpreter의 delta는 코드를 점진적으로 보여주는 용도. 전체 코드는 completed 이벤트의 result에 저장되어 있음. delta는 그때그때 업데이트
                    # 이쁘게 보여주기 위해 꾸며주기
                    elif event.data.type == 'response.code_interpreter_call.code.delta':
                        code_response += event.data.delta
                        code_placeholder.code(code_response)
                            
                    elif event.data.type == 'response.image_generation_call.partial_image':
                        image = base64.b64decode(event.data.partial_image_b64)
                        image_placeholder.image(image)
                                                                      
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
    if 'code_placeholder' in st.session_state:
        st.session_state['code_placeholder'].empty()
    if 'image_placeholder' in st.session_state:
        st.session_state['image_placeholder'].empty()
    if 'text_placeholder' in st.session_state:
        st.session_state['text_placeholder'].empty()

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