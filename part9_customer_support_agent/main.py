import dotenv

dotenv.load_dotenv()
from openai import OpenAI
import asyncio
import streamlit as st
from agents import Runner, SQLiteSession, function_tool, RunContextWrapper
from models import UserAccountContext


@function_tool
def get_user_tier(wrapper: RunContextWrapper[UserAccountContext]):

    # context에 들어있는 사용자 정보만 꺼내서, 툴이 필요한 최소 정보만 보게 한다.
    # 이렇게 하면 툴이 전체 메시지나 불필요한 데이터를 몰라도 된다.
    return (
        f"The user {wrapper.context.customer_id} has a {wrapper.context.tier} account."
    )


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

        async for event in stream.stream_events():
            if event.type == "raw_response_event":

                if event.data.type == "response.output_text.delta":
                    response += event.data.delta
                    text_placeholder.write(response.replace("$", "\$"))


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
