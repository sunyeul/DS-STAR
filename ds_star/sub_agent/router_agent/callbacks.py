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
        types.Part(text=f"# Question\n{question}"),
        types.Part(text=f"# Given data: {data_descriptions.keys()}"),
    ]
    for filename, summary in data_descriptions.items():
        parts.append(types.Part(text=f"{filename}\n{summary}\n"))

    parts.append(types.Part(text="# Current plans"))
    for i, plan in enumerate(plans, start=1):
        parts.append(types.Part(text=f"{i}. {plan}\n"))

    parts.append(
        types.Part(text=f"# Obtained results from the current plans:\n{result}")
    )
    parts.append(
        types.Part(
            text=f"""
# Your task
- If you think one of the steps of current plans is wrong, answer among the following options: Plan 1, Plan 2, ..., Plan {len(plans)}.
- If you think we should perform new NEXT plan, answer as 'Add Plan'.
- Your response should only be Plan 1 - Plan {len(plans)} or Add Plan. """
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
        yield types.Content(role="user", parts=[types.Part(text="Add Plan")])

    elif router_output.choice == "Modify Plan":
        plan_number = router_output.plan_number
        plans = state.get("plans")
        state["plans"] = plans[: plan_number - 1]
        yield types.Content(role="user", parts=[types.Part(text="Modify Plan")])
