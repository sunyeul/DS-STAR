from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

from .models import IsEnough


def verifier_before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    state = callback_context.session.state
    question = state.get("question")
    base_code = state.get("base_code")
    plans = state.get("plans")
    result = state.get("result")

    parts = [types.Part(text="# 計画")]
    for i, plan in enumerate(plans, start=1):
        parts.append(types.Part(text=f"{i}. {plan}\n"))

    parts.append(types.Part(text=f"# コード\n```python\n{base_code}\n```\n"))
    parts.append(types.Part(text=f"# コードの実行結果\n{result}\n"))
    parts.append(types.Part(text=f"# 質問\n{question}\n"))

    parts.append(
        types.Part(
            text="""# あなたのタスク
- 現在の計画とそのコード実装が質問に答えるのに十分かどうかを検証してください。
- 応答は'true'または'false'のいずれかである必要があります。
- 質問に答えるのに十分な場合は、'true'と答えてください。
- 質問に答えるのに不十分な場合は、'false'と答えてください。
"""
        )
    )
    llm_request.contents = [types.Content(role="user", parts=parts)]
    return None


def after_verifier_agent_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    state = callback_context.session.state
    is_enough = IsEnough.model_validate(obj=state.get("is_enough"))
    if is_enough.result:
        callback_context._event_actions.escalate = True
        return types.Content(
            role="user", parts=[types.Part(text="質問に答えるのに十分です。")]
        )
    else:
        return types.Content(
            role="user", parts=[types.Part(text="質問に答えるのに不十分です。")]
        )
