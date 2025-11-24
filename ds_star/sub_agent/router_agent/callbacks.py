from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

from .models import RouterOutput


def router_before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    state = callback_context.session.state
    question = state.get("question")
    data_descriptions = state.get("data_descriptions")
    plans = state.get("plans")
    result = state.get("result")

    parts = [
        types.Part(text=f"# 質問\n{question}"),
        types.Part(text=f"# 与えられたデータ: {data_descriptions.keys()}"),
    ]
    for filename, summary in data_descriptions.items():
        parts.append(types.Part(text=f"{filename}\n{summary}\n"))

    parts.append(types.Part(text="# 現在の計画"))
    for i, plan in enumerate(plans, start=1):
        parts.append(types.Part(text=f"{i}. {plan}\n"))

    parts.append(
        types.Part(text=f"# 現在の計画から得られた結果:\n{result}")
    )
    parts.append(
        types.Part(
            text=f"""
# あなたのタスク
- 現在の計画のステップの1つが間違っていると思う場合は、次のオプションから選択してください: Plan 1, Plan 2, ..., Plan {len(plans)}。
- 新しい次の計画を実行すべきだと思う場合は、'Add Plan'と答えてください。
- 応答は Plan 1 - Plan {len(plans)} または Add Plan のみである必要があります。 """
        ),
    )
    llm_request.contents = [
        types.Content(role="user", parts=parts),
    ]
    return None


def after_router_agent_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    state = callback_context.session.state
    router_output = RouterOutput.model_validate(obj=state.get("router_output"))

    if router_output.choice == "Add Plan":
        return types.Content(role="user", parts=[types.Part(text="計画を追加")])

    elif router_output.choice == "Modify Plan":
        plan_number = router_output.plan_number
        plans = state.get("plans")

        modified_plans = plans[: plan_number - 1]
        if len(modified_plans) > 0:
            state["current_plan"] = modified_plans[-1]
        else:
            state["current_plan"] = None

        state["plans"] = modified_plans
        return types.Content(role="user", parts=[types.Part(text="計画を修正")])
