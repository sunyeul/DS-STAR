from google.adk.agents import Agent

from .callbacks import finalyzer_before_model_callback

finalyzer_agent = Agent(
    model="gemini-2.5-flash",
    name="finalyzer_agent",
    description="質問への回答を最終化するファイナライザーエージェント。",
    instruction="""
あなたは専門のデータ分析者です。
以下にリストされたファイル/ドキュメントを読み込み、参照して事実質問に答えます。
また、参照コードも持っています。
あなたのタスクは、与えられたガイドラインに従って質問の答えを出力するソリューションコードを作成することです。
""",
    output_key="final_answer",
    before_model_callback=finalyzer_before_model_callback,
)
