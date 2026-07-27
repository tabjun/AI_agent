import dotenv

dotenv.load_dotenv()
from openai import OpenAI
import asyncio
import streamlit as st
from agents import Runner, SQLiteSession, InputGuardrailTripwireTriggered, function_tool, RunContextWrapper
from models import UserAccountContext


client = OpenAI()
 
user_account_ctx = UserAccountContext(
    customer_id=1,
    name="nico",
    tier="basic",
)


if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",
        "customer-support-memory.db",
    )
session = st.session_state["session"]


async def paint_history():
    messages = await session.get_items()
    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"].replace("$", "\$"))


asyncio.run(paint_history())


async def run_agent(message):
    
    with st.chat_message("ai"):
        text_placeholder = st.empty()
        response = ""

        st.session_state["text_placeholder"] = text_placeholder
        
        try:

            # context는 이 실행 1회에만 붙는 런타임 데이터다.
            # 같은 agent라도 어떤 context를 넣느냐에 따라 툴과 응답이 달라질 수 있다.
            stream = Runner.run_streamed(
                agent,
                message,
                session=session,
                # Runner에 context를 넣으면, Agent와 function_tool이 같은 사용자 문맥을 공유한다.
                # 즉, 요청마다 필요한 데이터만 주입할 수 있고, 하드코딩된 전역값에 덜 의존하게 된다.
                context=user_account_ctx,

            )

            # 설치된 SDK 기준 InputGuardrail의 run_in_parallel 기본값은 True라서,
            # 가드레일 판정과 모델의 응답 생성이 동시에 진행된다. 가드레일이 나중에 트립되어도
            # 이미 방출된 델타를 화면에 즉시 그려버리면, 걸러야 할 답변 일부가 사용자에게 노출된 뒤에야
            # 예외가 던져진다(세션에는 안 남지만 화면엔 이미 찍힌 상태). 그래서 델타는 버퍼에만 쌓아두고,
            # 스트림이 끝까지 가드레일 트립 없이 완료된 뒤에 한 번에 화면에 반영한다.
            async for event in stream.stream_events():
                if event.type == "raw_response_event":

                    if event.data.type == "response.output_text.delta":
                        response += event.data.delta

            text_placeholder.write(response.replace("$", "\$"))

        # 가드레일(triage_agent)에서 off-topic으로 판단되면, InputGuardrailTripwireTriggered 예외 발생. 에러 메세지 출력대신 이쁘게 가다듬기
        except InputGuardrailTripwireTriggered:
            st.write("I can't help you with that")

message = st.chat_input(
    "Write a message for your assistant",
)

if message:

    if "text_placeholder" in st.session_state:
        st.session_state["text_placeholder"].empty()

    if message:
        with st.chat_message("human"):
            st.write(message)
        asyncio.run(run_agent(message))


with st.sidebar:
    reset = st.button("Reset memory")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))
