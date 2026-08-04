import dotenv

dotenv.load_dotenv()
from openai import OpenAI
import asyncio
import streamlit as st
from agents import (Runner, SQLiteSession, InputGuardrailTripwireTriggered,
function_tool, RunContextWrapper, OutputGuardrailTripwireTriggered)
from models import UserAccountContext
from my_agents.triage_agent import triage_agent


client = OpenAI()
 
user_account_ctx = UserAccountContext(
    customer_id=1,
    name="태준",
    tier="basic",
    email="taejun@example.com",
)


if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",
        "customer-support-memory.db",
    )
session = st.session_state["session"]

if 'agent' not in st.session_state:
    st.session_state['agent'] = triage_agent

# SQLiteSession은 대화 메시지(role/content)만 저장하고 어떤 에이전트가 응답했는지는 기록하지 않는다.
# 사이드바에서 개발 확인용으로 보기 위해 handoff 이력을 따로 세션 상태에 쌓아둔다.
if 'agent_history' not in st.session_state:
    st.session_state['agent_history'] = [triage_agent.name]

# [메시지별 에이전트 매핑 코드] assistant 메시지의 id를 키로, 그 메시지를 만든 에이전트 이름을 값으로 저장한다.
# agent_history는 "언제 전환됐다"만 기록해서 어떤 대화(메시지)가 어떤 에이전트의 응답인지는 알 수 없었다.
# 메시지 id 단위로 매핑해두면 대화 내용과 에이전트를 1:1로 대응시켜 볼 수 있다.
if 'message_agent_map' not in st.session_state:
    st.session_state['message_agent_map'] = {}


async def paint_history():
    messages = await session.get_items()
    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    if message["type"] == "message":
                        # [메시지별 에이전트 매핑 코드] message_agent_map에서 이 메시지 id로 응답한
                        # 에이전트 이름을 찾아 캡션으로 보여준다. 매핑이 없으면(과거 세션에서 만들어진
                        # 메시지 등) "Unknown agent"로 표시한다.
                        agent_name = st.session_state["message_agent_map"].get(
                            message.get("id"), "Unknown agent"
                        )
                        st.caption(f"🤖 {agent_name}")
                        # "$"는 Python 문자열에서 유효한 이스케이프 문자가 아니라 SyntaxWarning이 뜬다.
                        # raw string(r"\$")으로 쓰면 경고 없이 같은 문자열(백슬래시+달러)을 만들 수 있다.
                        st.write(message["content"][0]["text"].replace("$", r"\$"))


asyncio.run(paint_history())


# 메세지를 보낼 때마다 triage_agent가 호출되어, off-topic 여부를 판단하고, 필요하면 handoff를 수행한다.
async def run_agent(message):
    
    with st.chat_message("ai"):
        # 여기에 empty 구문은 대화가 끝나면 새로운 대화창 열림. 에이전트 전환되는 거에서는 적용 안 됨.
        text_placeholder = st.empty()
        response = ""

        st.session_state["text_placeholder"] = text_placeholder
        
        try:

            # context는 이 실행 1회에만 붙는 런타임 데이터다.
            # 같은 agent라도 어떤 context를 넣느냐에 따라 툴과 응답이 달라질 수 있다.
            stream = Runner.run_streamed(
                st.session_state['agent'] ,
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
                        text_placeholder.write(response.replace("$", r"\$"))

                # line 27에서 if 문으로 정의한 st.session["agent"]을 시작으로, 매 요청 발생 시 에이전트 전환이 필요하면
                # 해당 line 82 elif 구문 덕분에 에이전트 전환 후 답변 가능
                elif event.type == 'agent_updated_stream_event':
                    
                    if st.session_state["agent"] != event.new_agent:
                        
                        # Agent는 클래스가 아니라 인스턴스라 __name__ 속성이 없다(그건 클래스/함수에만 있음).
                        # 사람이 읽을 이름은 인스턴스 필드인 .name 이다.
                        st.write(f'🤖Transfered from {st.session_state["agent"].name} to {event.new_agent.name}')
                        st.session_state["agent"] = event.new_agent
                        st.session_state["agent_history"].append(event.new_agent.name)

                        # 에이전트 전환되면 새로운 메세지 창 뜨게
                        text_placeholder.empty()
                        response = ""

            # [메시지별 에이전트 매핑 코드] 스트림이 끝난 뒤 이번 턴에서 실제로 최종 응답을 만든 에이전트는
            # stream.last_agent다(중간에 handoff가 여러 번 일어나도 마지막 에이전트가 여기 담긴다).
            # 방금 세션에 저장된 마지막 assistant 메시지의 id를 가져와 이 에이전트 이름과 매핑해둔다.
            saved_messages = await session.get_items()
            if saved_messages and saved_messages[-1].get("role") == "assistant":
                last_message_id = saved_messages[-1].get("id")
                st.session_state["message_agent_map"][last_message_id] = stream.last_agent.name

        # 가드레일(triage_agent)에서 off-topic으로 판단되면, InputGuardrailTripwireTriggered 예외 발생. 에러 메세지 출력대신 이쁘게 가다듬기
        except InputGuardrailTripwireTriggered:
            st.write("I can't help you with that")
            
        except OutputGuardrailTripwireTriggered:
            st.write("can't answer your question because it contains information outside my domain. Please ask a different question.")

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
        st.session_state["agent"] = triage_agent
        st.session_state["agent_history"] = [triage_agent.name]
        # [메시지별 에이전트 매핑 코드] 세션을 지우면 매핑도 같이 비워야 다음 대화에서 엉뚱한 과거 매핑이 남지 않는다.
        st.session_state["message_agent_map"] = {}

    st.write("Current agent:", st.session_state["agent"].name)
    st.write("Agent history:", st.session_state["agent_history"])
    # [메시지별 에이전트 매핑 코드] 메시지 id -> 응답한 에이전트 이름 매핑을 개발 확인용으로 그대로 노출한다.
    st.write("Message-to-agent map:", st.session_state["message_agent_map"])
    st.write(asyncio.run(session.get_items()))
