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
    初期コード生成と後続コード修正を動的に処理する統合コーダーエージェント。
    """

    initial_agent: Agent
    next_step_agent: Agent

    def __init__(self, name: str = "coder_agent"):
        initial_agent = Agent(
            model="gemini-2.5-flash",
            name="initial_coder_impl",  # 内部識別用の名前
            description="最初のステップをコーディングする初期コーダーエージェント。",
            output_key="base_code",
            output_schema=ExecutableCode,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            before_model_callback=initial_coder_before_model_callback,
            after_agent_callback=after_coder_agent_callback,
        )

        next_step_agent = Agent(
            model="gemini-2.5-flash",
            name="coder_impl",  # 内部識別用の名前
            description="次のステップをコーディングするコーダーエージェント。",
            instruction="""
            あなたは専門のデータ分析者です。
            あなたのタスクは、与えられたデータで現在の計画を実装することです。
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
        現在のセッション状態（以前のコードの存在有無）を確認し、適切なエージェントに実行を委譲します。
        """

        current_code = ctx.session.state.get("base_code")

        if not current_code:
            selected_agent = self.initial_agent
        else:
            selected_agent = self.next_step_agent

        async for event in selected_agent.run_async(ctx):
            yield event


coder_agent = CoderAgent()
