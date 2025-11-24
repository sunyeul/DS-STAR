from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types


def finalyzer_before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    state = callback_context.session.state
    question = state.get("question")
    data_descriptions = state.get("data_descriptions")
    base_code = state.get("base_code")
    result = state.get("result")

    parts = [
        types.Part(text=f"# 質問\n{question}"),
    ]

    parts.append(types.Part(text=f"# 与えられたデータ: {data_descriptions.keys()}"))
    for filename, summary in data_descriptions.items():
        parts.append(types.Part(text=f"{filename}\n{summary}\n"))
    parts.append(types.Part(text=f"# 参照コード\n```python\n{base_code}\n```\n"))
    parts.append(types.Part(text=f"# 参照コードの実行結果\n{result}\n"))

    parts.append(
        types.Part(
            text="""# あなたのタスク
- 与えられたガイドラインに従って答えを出力するようにソリューションコードを修正してください。
- 答えが参照コードの実行結果から得られる場合は、希望する答えを出力するPythonコードを生成してください。
- コードは単一ファイルのPythonプログラムで、自己完結型であり、そのまま実行可能である必要があります。
- 応答には単一のコードブロックのみを含めてください。
- エラーが発生した場合にデバッグするため、ダミーの内容を含めないでください。
- エラーを防ぐためにtry:とexcept:を使用しないでください。後でデバッグします。
- すべてのファイル/ドキュメントは`data/`ディレクトリにあります。
"""
        )
    )
    llm_request.contents = [
        types.Content(role="user", parts=parts),
    ]
    return None
