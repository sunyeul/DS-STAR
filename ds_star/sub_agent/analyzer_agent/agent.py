from google.adk.agents import LlmAgent

from config import PathsConfig

from .callback import after_analyzer_agent_callback
from .models import ExecutableCode

paths_config = PathsConfig()

# エージェント定義
analyzer_agent = LlmAgent(
    name="analyzer_agent",
    model="gemini-2.5-flash",
    instruction="""
あなたは専門のデータ分析者です。
{filename}の内容を読み込み、説明するPythonコードを生成してください。

# 要件
- ファイルは構造化データまたは非構造化データのいずれでも可能です。
- 構造化データが多すぎる場合は、数例のみを出力してください。
- 重要な情報を出力してください。例えば、すべての列名を出力してください。
- Pythonコードは{filename}の内容を出力する必要があります。
- コードは単一ファイルのPythonプログラムで、自己完結型であり、そのまま実行可能である必要があります。
- 応答には単一のコードブロックのみを含めてください。
- 重要: エラーが発生した場合にデバッグするため、ダミーの内容を含めないでください。
- エラーを防ぐためにtry:とexcept:を使用しないでください。後でデバッグします。
    """,
    description="ファイルの内容を分析し、内容を説明するPythonコードを生成します。",
    output_key="executable_code",
    output_schema=ExecutableCode,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    after_agent_callback=after_analyzer_agent_callback,
)
