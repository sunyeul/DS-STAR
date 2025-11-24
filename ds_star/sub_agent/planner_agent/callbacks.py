from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types


def initial_planner_before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    state = callback_context.session.state
    question = state.get("question")
    data_descriptions = state.get("data_descriptions")

    parts = [
        types.Part(text="# 質問"),
        types.Part(text=question),
        types.Part(text=f"# 与えられたデータ: {data_descriptions.keys()}"),
    ]
    for filename, summary in data_descriptions.items():
        parts.append(types.Part(text=f"{filename}\n{summary}\n"))
    parts.append(
        types.Part(
            text="""# あなたのタスク
- 上記の質問に答えるための最初のステップを提案してください。
- 最初のステップは質問に答えるのに十分である必要はありません。
- 質問に答えるための良い出発点となる、非常にシンプルな初期ステップを提案してください。
"""
        )
    )

    llm_request.contents = [
        types.Content(
            role="user",
            parts=parts,
        )
    ]
    return None


def planner_before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    state = callback_context.session.state
    question = state.get("question")
    data_descriptions = state.get("data_descriptions")
    plans = state.get("plans")
    result = state.get("result")

    parts = [
        types.Part(text="# 質問"),
        types.Part(text=question),
    ]

    for filename, summary in data_descriptions.items():
        parts.append(types.Part(text=f"{filename}\n{summary}\n"))

    parts.append(types.Part(text="# 現在の計画"))
    for i, plan in enumerate(plans, start=1):
        parts.append(types.Part(text=f"{i}. {plan}\n"))

    parts.append(types.Part(text="# 現在の計画から得られた結果:"))
    parts.append(types.Part(text=result))

    parts.append(
        types.Part(
            text="""# あなたのタスク
- 上記の質問に答えるための次のステップを提案してください。
- 次のステップは質問に答えるのに十分である必要はありませんが、最後のシンプルなステップのみが必要な場合は、それを提案しても構いません。
- 質問に答えるための良い中間地点となる、非常にシンプルな次のステップを提案してください。
- もちろん、あなたの応答は質問に直接答えることができる計画でも構いません。
"""
        )
    )

    llm_request.contents = [
        types.Content(
            role="user",
            parts=parts,
        )
    ]
    return None


def append_plan(callback_context: CallbackContext) -> Optional[types.Content]:
    state = callback_context.session.state
    current_plan = state.get("current_plan")
    if "plans" not in state:
        state["plans"] = [current_plan]
    else:
        state["plans"].append(current_plan)
    return None
