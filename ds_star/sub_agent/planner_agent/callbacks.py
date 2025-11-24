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
        types.Part(text="# Question"),
        types.Part(text=question),
        types.Part(text=f"# Given data: {data_descriptions.keys()}"),
    ]
    for filename, summary in data_descriptions.items():
        parts.append(types.Part(text=f"{filename}\n{summary}\n"))
    parts.append(
        types.Part(
            text="""# Your task
- Suggest your very first step to answer the question above.
- Your first step does not need to be sufficient to answer the question.
- Just propose a very simple initial step, which can act as a good starting point to answer the question.
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
        types.Part(text="# Question"),
        types.Part(text=question),
    ]

    for filename, summary in data_descriptions.items():
        parts.append(types.Part(text=f"{filename}\n{summary}\n"))

    parts.append(types.Part(text="# Current plans"))
    for i, plan in enumerate(plans, start=1):
        parts.append(types.Part(text=f"{i}. {plan}\n"))

    parts.append(types.Part(text="# Obtained results from the current plans:"))
    parts.append(types.Part(text=result))

    parts.append(
        types.Part(
            text="""# Your task
- Suggest your next step to answer the question above.
- Your next step does not need to be sufficient to answer the question, but if it requires only final simple last step you may suggest it.
- Just propose a very simple next step, which can act as a good intermediate point to answer the question.
- Of course your response can be a plan which could directly answer the question.
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
