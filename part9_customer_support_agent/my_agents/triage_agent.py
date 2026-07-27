'''
역할 명세
 1. 유저의 입력을 받고, 올바른 에이전트한테 전달하는 역할
 2. 질문을 살펴보고 주제와 관련 없거나, 무례함 등 에티켓에 어긋나는 질문은 거절하고, 관련 있는 질문은 적절한 에이전트에게 전달
 '''

from agents import (
    Agent,
    RunContextWrapper,
    input_guardrail,
    Runner,
    GuardrailFunctionOutput,
    handoff,
    )
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from agents.extensions import handoff_filters
from models import UserAccountContext, InputGuardRailOutput, HandoffData
from my_agents.account_agent import account_agent
from my_agents.technical_agent import technical_agent
from my_agents.order_agent import order_agent
from my_agents.billing_agent import billing_agent

import streamlit as st


# 안전 설정으로 AI 가 정형화된 범위 내에서만 동작하도록 제한하는 에이전트 정의
input_guardrail_agent = Agent(
    name = "Input Guardrail Agent",
    # 규칙 정의
     instructions="""
    Ensure the user's request specifically pertains to User Account details, 
    Billing inquiries, Order information, or Technical Support issues, and is not off-topic.
    If the request is off-topic, return a reason for the tripwire.   
    You can make small conversation with the user, specially at the beginning of the conversation, 
    but don't help with requests that are not related to User Account details, Billing inquiries, Order information,
    or Technical Support issues.
""",
    output_type = InputGuardRailOutput
)

# 실제로 에이전트가 실행될 함수
@input_guardrail
async def off_topic_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext], 
    input: str, # 유저가 입력한 내용
    ):
    result = await Runner.run(input_guardrail_agent, input, context=wrapper.context) # context에는 래핑된 값이 들어옴
    # input/output guardrail은 아래 함수 무조건 반환해야 함(지금은 데코레이터)
    return GuardrailFunctionOutput(
        output_info = result.final_output,
        tripwire_triggered=result.final_output.is_off_topic # 이것도 필수
    )

# 동적으로 triage_agent 지침 내려주는 함수
# 동일 함수를 여러 에이전트에 활용 가능하기 때문에 여기에도 에이전트 정의
def dynamic_triage_agent_instructinos(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
    ):
    
    # 어떤 에이전트가 이 함수를 호출하는지 알게 하려면
    # if agent.name == 'Triage Agent':
    # return ~~~ => 이렇게 작성해서 triage_agent를 위한 지침 생성 가능
    
    # 지금 강의에서는 UserAccountContext에 입력되는 프롬프트를 활용해서 지침을 내려주는 예시를 보여주기 위해, agent.name을 활용하지 않고 작성함.
    return f"""

    {RECOMMENDED_PROMPT_PREFIX}
    You are a customer support agent. You ONLY help customers with their questions about their User Account, Billing, Orders, or Technical Support.
    You call customers by their name.
    
    The customer's name is {wrapper.context.name}. 
    The customer's email is {wrapper.context.email}.
    The customer's tier is {wrapper.context.tier}.
    
    YOUR MAIN JOB: Classify the customer's issue and route them to the right specialist.
    
    ISSUE CLASSIFICATION GUIDE:
    
    🔧 TECHNICAL SUPPORT - Route here for:
    - Product not working, errors, bugs
    - App crashes, loading issues, performance problems
    - Feature questions, how-to help
    - Integration or setup problems
    - "The app won't load", "Getting error message", "How do I..."
    
    💰 BILLING SUPPORT - Route here for:
    - Payment issues, failed charges, refunds
    - Subscription questions, plan changes, cancellations
    - Invoice problems, billing disputes
    - Credit card updates, payment method changes
    - "I was charged twice", "Cancel my subscription", "Need a refund"
    
    📦 ORDER MANAGEMENT - Route here for:
    - Order status, shipping, delivery questions
    - Returns, exchanges, missing items
    - Tracking numbers, delivery problems
    - Product availability, reorders
    - "Where's my order?", "Want to return this", "Wrong item shipped"
    
    👤 ACCOUNT MANAGEMENT - Route here for:
    - Login problems, password resets, account access
    - Profile updates, email changes, account settings
    - Account security, two-factor authentication
    - Account deletion, data export requests
    - "Can't log in", "Forgot password", "Change my email"
    
    CLASSIFICATION PROCESS:
    1. Listen to the customer's issue
    2. Ask clarifying questions if the category isn't clear
    3. Classify into ONE of the four categories above
    4. Explain why you're routing them: "I'll connect you with our [category] specialist who can help with [specific issue]"
    5. Route to the appropriate specialist agent
    
    SPECIAL HANDLING:
    - Premium/Enterprise customers: Mention their priority status when routing
    - Multiple issues: Handle the most urgent first, note others for follow-up
    - Unclear issues: Ask 1-2 clarifying questions before routing
    """

# handoff가 발생할 때마다 실행되는 함수 만들기 
def handle_handoff(
    # 이렇게 정의하면 ~~ userID에 의해 ~ handoff가 발생했음 파악 가능
    wrapper: RunContextWrapper[UserAccountContext],
    input_data: HandoffData, # handoff 발생 시, 어떤 에이전트에게 handoff 되었는지, 어떤 이유로 handoff 되었는지 등 에이전트 간 handoff를 기록할 수 있는 데이터 모델 정의
):
    # 화면 내 사이드바로 구현
    with st.sidebar:
        st.write(f'''
                 Handing off to {input_data.to_agent_name}
                 Reason: {input_data.reason}
                 Issue Type: {input_data.issue_type}
                 Issue Description: {input_data.issue_description}

                 ''')

def make_handoff(agent):
    
    return handoff(
            agent=agent,
            on_handoff = handle_handoff,
            input_type = HandoffData,
            # handoff 발생 시, 어떤 에이전트에게 handoff 되었는지, 어떤 이유로 handoff 되었는지 등 에이전트 간 handoff를 기록할 수 있는 데이터 모델 정의
            input_filter = handoff_filters.remove_all_tools,
        
    )


# 현재 설치된 openai-agents SDK 버전에서는 Agent의 필드명이 input_guardrails(복수형)이다.
# 강의에서 쓰던 input_guardrail(단수형)로 넘기면 dataclass에 없는 필드라 조용히 무시되고,
# off_topic_guardrail이 triage_agent에 아예 연결되지 않아 가드레일이 동작하지 않는다.
triage_agent = Agent(
    name="Triage Agent",
    instructions = dynamic_triage_agent_instructinos,
    input_guardrails = [off_topic_guardrail],
    # 각 에이전트에게 명령 하달, handoffs
    # 에이전트를 묶어서 tool처럼 사용 가능하게
    
    handoffs = [
        make_handoff(technical_agent),
        make_handoff(billing_agent),
        make_handoff(order_agent),
        make_handoff(account_agent),
                ],
    
    # 이 방식은 특정 손님에게 전담으로 에이전트 연결해줄때 유용함
    # tools = [technical_agent.as_tool(
    #     tool_name= 'Technical Support Agent',
    #     tool_description = 'Use This when the user needs tech support'
    # )],

)
