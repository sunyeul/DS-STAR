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
        types.Part(text=f"# Question\n{question}"),
    ]

    parts.append(types.Part(text=f"# Given data: {data_descriptions.keys()}"))
    for filename, summary in data_descriptions.items():
        parts.append(types.Part(text=f"{filename}\n{summary}\n"))
    parts.append(types.Part(text=f"# Reference code\n```python\n{base_code}\n```\n"))
    parts.append(types.Part(text=f"#  Execution result of reference code\n{result}\n"))

    parts.append(
        types.Part(
            text="""# Your task
- Modify the solution code to print out answer to follow the give guidelines.
- If the answer can be obtained from the execution result of the reference code, just generate a Python code that prints out the desired answer.
- The code should be a single-file Python program that is self-contained and can be executed as-is.
- Your response should only contain a single code block.
- Do not include dummy contents since we will debug if error occurs.
- Do not use try: and except: to prevent error. I will debug it later.
- All files/documents are in `data/` directory.
"""
        )
    )
    llm_request.contents = [
        types.Content(role="user", parts=parts),
    ]
    return None
