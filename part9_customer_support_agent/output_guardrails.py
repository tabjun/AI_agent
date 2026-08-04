from agents import Agent, output_guardrail, Runner, RunContextWrapper, GuardrailFunctionOutput
from models import DomainLeakageGuardRailOutput, UserAccountContext


# 4개 도메인 가드레일이 반복해서 만드는 것: (1) 판정용 서브 에이전트, (2) 그 에이전트를 돌려서
# 자기 도메인 필드를 뺀 나머지가 하나라도 true면 trip시키는 @output_guardrail 함수.
# 매번 손으로 복붙하는 대신 아래 두 팩토리로 만들어서, 도메인 이름/설명만 바꾸면 되게 규격화했다.
def make_domain_guardrail_agent(domain_label: str, own_domain_description: str) -> Agent:
    return Agent(
        name=f"{domain_label} Support Guardrail",
        instructions=f"""
        Analyze the {domain_label.lower()} support response to check if it inappropriately contains
        information outside this agent's domain ({own_domain_description}):
        - Technical support info (diagnostics, troubleshooting steps, engineering escalation)
        - Billing info (payments, refunds, charges, subscriptions)
        - Order info (shipping, tracking, delivery, returns)
        - Account management info (passwords, email changes, account settings)

        {domain_label} agents should ONLY provide {own_domain_description}.
        Mark the field for THIS agent's own domain as false (it's expected to appear there);
        only flag the OTHER three domains as true when their content leaks in.
        Return true for any field that contains content outside this agent's domain.
        """,
        output_type=DomainLeakageGuardRailOutput,
    )


def make_output_guardrail(guardrail_agent: Agent, *own_domain_fields: str):
    @output_guardrail
    async def _domain_output_guardrail(
        wrapper: RunContextWrapper[UserAccountContext],
        agent: Agent,
        output: str,
    ):
        result = await Runner.run(
            guardrail_agent,
            output,
            context=wrapper.context,
        )

        validation = result.final_output
        # own_domain_fields(이 에이전트가 담당하는 도메인)를 제외한 나머지가 하나라도 true면 범위 이탈.
        triggered = validation.leaks_outside(*own_domain_fields)

        # GuardrailFunctionOutput은 output_info/tripwire_triggered 두 필드만 받는다(tripwire_reason은
        # 없는 필드라 넘기면 TypeError). 트립 사유는 output_info에 담긴 validation.reason으로 이미 확인 가능하다.
        return GuardrailFunctionOutput(
            output_info=validation,
            tripwire_triggered=triggered,
        )

    return _domain_output_guardrail


technical_output_guardrail_agent = make_domain_guardrail_agent(
    "Technical Support", "technical troubleshooting, diagnostics, and product support"
)
technical_output_guardrail = make_output_guardrail(
    technical_output_guardrail_agent, "contains_technical_data"
)

billing_output_guardrail_agent = make_domain_guardrail_agent(
    "Billing Support", "billing, payment, and subscription support"
)
billing_output_guardrail = make_output_guardrail(
    billing_output_guardrail_agent, "contains_billing_data"
)

order_output_guardrail_agent = make_domain_guardrail_agent(
    "Order Management", "order status, shipping, and returns support"
)
order_output_guardrail = make_output_guardrail(
    order_output_guardrail_agent, "contains_order_data"
)

account_output_guardrail_agent = make_domain_guardrail_agent(
    "Account Management", "account access, security, and profile management support"
)
account_output_guardrail = make_output_guardrail(
    account_output_guardrail_agent, "contains_account_data"
)