import os
import subprocess
import tempfile
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

from config import PathsConfig

from .models import ExecutableCode

paths_config = PathsConfig()


def _run_temp_python(code: str) -> str:
    # temp 파일을 먼저 완전히 닫은 뒤 실행
    with tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        suffix=".py",
        dir=paths_config.data_dir,
        encoding="utf-8",
    ) as tmp:
        tmp.write(code)
        tmp.flush()
        temp_path = tmp.name

    try:
        result = subprocess.run(
            ["uv", "run", "python", temp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=paths_config.data_dir,
        )
        execution_output = result.stdout + "\n" + result.stderr
        return execution_output
    finally:
        os.remove(temp_path)


def after_coder_agent_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    state = callback_context.session.state
    base_code = ExecutableCode.model_validate(obj=state.get("base_code"))
    result = _run_temp_python(code=base_code.code)

    state["result"] = result
    return types.Content(role="user", parts=[types.Part(text=result)])


def initial_coder_before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    state = callback_context.session.state
    data_descriptions = state.get("data_descriptions")
    current_plan = state.get("current_plan")

    parts = [
        types.Part(text=f"# Given data: {data_descriptions.keys()}"),
    ]
    for filename, summary in data_descriptions.items():
        parts.append(types.Part(text=f"{filename}\n{summary}\n"))
    parts.append(types.Part(text=f"# Current plan\n{current_plan}\n"))
    parts.append(
        types.Part(
            text="""
# Your task
- Implement the plan with the given data.
- Your response should be a single markdown Python code (wrapped in ```).
- There should be no additional headings or text in your response.
"""
        )
    )

    llm_request.contents = [
        types.Content(role="user", parts=parts),
    ]
    return None


def coder_before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    state = callback_context.session.state
    data_descriptions = state.get("data_descriptions")
    base_code = state.get("base_code")
    previous_plans = state.get("plans")[:-1]
    current_plan = state.get("current_plan")

    parts = [
        types.Part(text=f"# Given data: {data_descriptions.keys()}"),
    ]
    for filename, summary in data_descriptions.items():
        parts.append(types.Part(text=f"{filename}\n{summary}\n"))
    parts.append(types.Part(text=f"# Base code\n```python\n{base_code}\n```\n"))
    parts.append(types.Part(text="# Previous plans"))
    for i, plan in enumerate(previous_plans, start=1):
        parts.append(types.Part(text=f"{i}. {plan}\n"))
    parts.append(types.Part(text=f"# Current plan to implement\n{current_plan}\n"))
    parts.append(
        types.Part(
            text="""
# Your task
- Implement the current plan with the given data.
- Your response should be a single markdown Python code (wrapped in ```).
- There should be no additional headings or text in your response.
"""
        )
    )

    llm_request.contents = [
        types.Content(role="user", parts=parts),
    ]
    return None
