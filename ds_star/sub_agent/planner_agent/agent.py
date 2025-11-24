from typing import AsyncGenerator

from google.adk.agents import Agent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from .callbacks import (
    append_plan,
    initial_planner_before_model_callback,
    planner_before_model_callback,
)


class PlannerAgent(BaseAgent):
    """
    初期計画と後続計画の策定を動的に処理する統合プランナーエージェント。
    """

    initial_agent: Agent
    next_step_agent: Agent

    def __init__(self, name: str = "planner_agent"):
        initial_agent = Agent(
            model="gemini-2.5-flash",
            name="initial_planner_impl",  # 内部識別用の名前
            description="最初のステップを計画する初期プランナーエージェント。",
            instruction="""
            あなたは専門のデータ分析者です。
            与えられたデータに基づいて事実質問に答えるためには、まず効果的に計画を立てる必要があります。
            """,
            output_key="current_plan",
            before_model_callback=initial_planner_before_model_callback,
            after_agent_callback=append_plan,
        )

        next_step_agent = Agent(
            model="gemini-2.5-flash",
            name="planner_impl",  # 内部識別用の名前
            description="次のステップを計画するプランナーエージェント。",
            instruction="""
            あなたは専門のデータ分析者です。
            与えられたデータに基づいて事実質問に答えるためには、まず効果的に計画を立てる必要があります。
            あなたのタスクは、質問に答えるために次に行うべき計画を提案することです。
            """,
            output_key="current_plan",
            before_model_callback=planner_before_model_callback,
            after_agent_callback=append_plan,
        )
        super().__init__(
            name=name, initial_agent=initial_agent, next_step_agent=next_step_agent
        )

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        現在のセッション状態（計画の存在有無）を確認し、適切なエージェントに実行を委譲します。
        """
        plans = ctx.session.state.get("plans", [])

        if len(plans) == 0:
            selected_agent = self.initial_agent
        else:
            selected_agent = self.next_step_agent

        async for event in selected_agent.run_async(ctx):
            yield event


planner_agent = PlannerAgent()
