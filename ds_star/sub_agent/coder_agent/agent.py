from typing import AsyncGenerator

from google.adk.agents import Agent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from config import PathsConfig

from .callbacks import (
    after_coder_agent_callback,
    coder_before_model_callback,
    initial_coder_before_model_callback,
)
from .models import ExecutableCode

paths_config = PathsConfig()


class CoderAgent(BaseAgent):
    """
    초기 코드 생성과 후속 코드 수정을 동적으로 처리하는 통합 코더 에이전트.
    """

    initial_agent: Agent
    next_step_agent: Agent

    def __init__(self, name: str = "coder_agent"):
        initial_agent = Agent(
            model="gemini-2.5-flash",
            name="initial_coder_impl",  # 내부 식별용 이름
            description="An initial coder agent that codes the first step.",
            output_key="base_code",
            output_schema=ExecutableCode,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            before_model_callback=initial_coder_before_model_callback,
            after_agent_callback=after_coder_agent_callback,
        )

        next_step_agent = Agent(
            model="gemini-2.5-flash",
            name="coder_impl",  # 내부 식별용 이름
            description="A coder agent that codes the next step.",
            instruction="""
            You are an expert data analysist.
            Your task is to implement the current plan with the given data.
            """,
            output_key="base_code",
            output_schema=ExecutableCode,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            before_model_callback=coder_before_model_callback,
            after_agent_callback=after_coder_agent_callback,
        )
        super().__init__(
            name=name, initial_agent=initial_agent, next_step_agent=next_step_agent
        )

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        현재 세션 상태(이전 코드 존재 여부)를 확인하여 적절한 에이전트에게 실행을 위임합니다.
        """

        current_code = ctx.session.state.get("base_code")

        if not current_code:
            selected_agent = self.initial_agent
        else:
            selected_agent = self.next_step_agent

        async for event in selected_agent.run_async(ctx):
            yield event


coder_agent = CoderAgent()
