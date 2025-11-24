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
    초기 계획과 후속 계획 수립을 동적으로 처리하는 통합 플래너 에이전트.
    """

    initial_agent: Agent
    next_step_agent: Agent

    def __init__(self, name: str = "planner_agent"):
        initial_agent = Agent(
            model="gemini-2.5-flash",
            name="initial_planner_impl",  # 내부 식별용 이름 변경
            description="An initial planner agent that plans the first step.",
            instruction="""
            You are an expert data analyst.
            In order to answer factoid questions based on the given data, you have to first plan effectively.
            """,
            output_key="current_plan",
            before_model_callback=initial_planner_before_model_callback,
            after_agent_callback=append_plan,
        )

        next_step_agent = Agent(
            model="gemini-2.5-flash",
            name="planner_impl",  # 내부 식별용 이름 변경
            description="A planner agent that plans the next step.",
            instruction="""
            You are an expert data analyst.
            In order to answer factoid questions based on the given data, you have to first plan effectively.
            Your task is to suggest next plan to do to answer the question.
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
        현재 세션 상태(계획 존재 여부)를 확인하여 적절한 에이전트에게 실행을 위임합니다.
        """
        plans = ctx.session.state.get("plans", [])

        if len(plans) == 0:
            selected_agent = self.initial_agent
        else:
            selected_agent = self.next_step_agent

        async for event in selected_agent.run_async(ctx):
            yield event


planner_agent = PlannerAgent()
