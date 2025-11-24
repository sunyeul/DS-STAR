from typing import AsyncGenerator

from google.adk.agents import Agent, BaseAgent, LoopAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from config import PathsConfig

from .sub_agent.analyzer_agent import analyzer_agent
from .sub_agent.coder_agent import coder_agent
from .sub_agent.finalyzer_agent import finalyzer_agent
from .sub_agent.planner_agent import planner_agent
from .sub_agent.router_agent import router_agent
from .sub_agent.verifier_agent import verifier_agent

paths_config = PathsConfig()


class DSStarAgent(BaseAgent):
    analyzer_agent: Agent
    planner_agent: BaseAgent
    coder_agent: BaseAgent
    verifier_agent: Agent
    router_agent: Agent

    finalyzer_agent: Agent
    # ワークフローエージェント
    loop_agent: LoopAgent

    def __init__(
        self,
        name: str,
        description: str,
        analyzer_agent: Agent,
        planner_agent: BaseAgent,
        coder_agent: BaseAgent,
        verifier_agent: Agent,
        router_agent: Agent,
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
            planner_agent=planner_agent,
            coder_agent=coder_agent,
            verifier_agent=verifier_agent,
            router_agent=router_agent,
            finalyzer_agent=finalyzer_agent,
            # ワークフロー
            loop_agent=loop_agent,
        )

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        print("DSStarAgentを実行中")
        ctx.user_content
        state = ctx.session.state

        # データファイルの分析
        for file in paths_config.data_dir.glob("*"):
            print(f"ファイルを分析中: {file.name}")
            state["filename"] = file.name
            async for event in self.analyzer_agent.run_async(ctx):
                yield event

        # 初期ステップの計画
        async for event in self.planner_agent.run_async(ctx):
            yield event

        # 初期ステップのコーディング
        async for event in self.coder_agent.run_async(ctx):
            yield event

        # ループの実行
        async for event in self.loop_agent.run_async(ctx):
            yield event

        # 回答の最終化
        async for event in self.finalyzer_agent.run_async(ctx):
            yield event


ds_star_agent = DSStarAgent(
    name="ds_star_agent",
    description="データを分析し、質問に答えるための次のステップを計画するDSStarエージェント。",
    analyzer_agent=analyzer_agent,
    planner_agent=planner_agent,
    coder_agent=coder_agent,
    verifier_agent=verifier_agent,
    router_agent=router_agent,
    finalyzer_agent=finalyzer_agent,
)

root_agent = ds_star_agent
