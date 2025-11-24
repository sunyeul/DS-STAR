from google.adk.agents import Agent

from .callbacks import router_before_model_callback
from .models import RouterOutput

router_agent = Agent(
    model="gemini-2.5-flash",
    name="router_agent",
    description="質問を適切なエージェントにルーティングするルーターエージェント。",
    instruction="""
あなたは専門のデータ分析者です。
現在の計画では質問に答えるのに不十分なため、あなたのタスクは質問に答えるために計画をどのように改善するかを決定することです。
""",
    output_key="router_output",
    output_schema=RouterOutput,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    before_model_callback=router_before_model_callback,
)
