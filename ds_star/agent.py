from typing import AsyncGenerator

from google.adk.agents import Agent, BaseAgent, LoopAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from config import PathsConfig

from .sub_agent.analyzer_agent import analyzer_agent
from .sub_agent.coder_agent import coder_agent, initial_coder_agent
from .sub_agent.finalyzer_agent import finalyzer_agent
from .sub_agent.planner_agent import initial_planner_agent, planner_agent
from .sub_agent.router_agent import router_agent
from .sub_agent.verifier_agent import verifier_agent

paths_config = PathsConfig()


class DSStarAgent(BaseAgent):
    analyzer_agent: Agent
    initial_planner_agent: Agent
    initial_coder_agent: Agent
    verifier_agent: Agent
    router_agent: Agent
    planner_agent: Agent
    coder_agent: Agent
    finalyzer_agent: Agent
    # workflow agent
    loop_agent: LoopAgent

    def __init__(
        self,
        name: str,
        description: str,
        analyzer_agent: Agent,
        initial_planner_agent: Agent,
        initial_coder_agent: Agent,
        verifier_agent: Agent,
        router_agent: Agent,
        planner_agent: Agent,
        coder_agent: Agent,
        finalyzer_agent: Agent,
    ):
        loop_agent = LoopAgent(
            name="LoopAgent",
            sub_agents=[
                verifier_agent,
                router_agent,
                planner_agent,
                coder_agent,
            ],
            max_iterations=5,
        )
        super().__init__(
            name=name,
            description=description,
            analyzer_agent=analyzer_agent,
            initial_planner_agent=initial_planner_agent,
            initial_coder_agent=initial_coder_agent,
            verifier_agent=verifier_agent,
            router_agent=router_agent,
            planner_agent=planner_agent,
            coder_agent=coder_agent,
            finalyzer_agent=finalyzer_agent,
            # workflow
            loop_agent=loop_agent,
        )

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        print("Running DSStarAgent")
        ctx.user_content
        state = ctx.session.state

        # Analyzing data files
        for file in paths_config.data_dir.glob("*"):
            print(f"Analyzing file: {file.name}")
            state["filename"] = file.name
            async for event in self.analyzer_agent.run_async(ctx):
                yield event

        # Planning the next step
        async for event in self.initial_planner_agent.run_async(ctx):
            yield event

        # Coding the next step
        async for event in self.initial_coder_agent.run_async(ctx):
            yield event

        # Running the loop
        async for event in self.loop_agent.run_async(ctx):
            yield event

        # Finalizing the answer
        async for event in self.finalyzer_agent.run_async(ctx):
            yield event


ds_star_agent = DSStarAgent(
    name="ds_star_agent",
    description="A DSStar agent that analyzes the data and plans the next step to answer the question.",
    analyzer_agent=analyzer_agent,
    initial_planner_agent=initial_planner_agent,
    initial_coder_agent=initial_coder_agent,
    verifier_agent=verifier_agent,
    router_agent=router_agent,
    planner_agent=planner_agent,
    coder_agent=coder_agent,
    finalyzer_agent=finalyzer_agent,
)

root_agent = ds_star_agent
