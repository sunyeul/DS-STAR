from google.adk.agents import Agent

from .callbacks import after_verifier_agent_callback, verifier_before_model_callback
from .models import IsEnough

verifier_agent = Agent(
    model="gemini-2.5-flash",
    name="verifier_agent",
    description="現在の計画とそのコード実装が質問に答えるのに十分かどうかを検証する検証エージェント。",
    instruction="""
あなたは専門のデータ分析者です。
あなたのタスクは、現在の計画とそのコード実装が質問に答えるのに十分かどうかを確認することです。
""",
    output_key="is_enough",
    output_schema=IsEnough,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    before_model_callback=verifier_before_model_callback,
    after_agent_callback=after_verifier_agent_callback,
)
