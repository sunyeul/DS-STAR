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

    parts = [types.Part(text="# Plan")]
    for i, plan in enumerate(plans, start=1):
        parts.append(types.Part(text=f"{i}. {plan}\n"))

    parts.append(types.Part(text=f"# Code\n```python\n{base_code}\n```\n"))
    parts.append(types.Part(text=f"# Execution result of code\n{result}\n"))
    parts.append(types.Part(text=f"# Question\n{question}\n"))

    parts.append(
        types.Part(
            text="""# Your task
- Verify whether the current plan and its code implementation is enough to answer the question.
- Your response should be one of 'true' or 'false'.
- If it is enough to answer the question, please answer 'true'.
- If it is not enough to answer the question, please answer 'false'.
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
            role="user", parts=[types.Part(text="Sufficient to answer the question.")]
        )
    else:
        return types.Content(
            role="user", parts=[types.Part(text="Insufficient to answer the question.")]
        )
