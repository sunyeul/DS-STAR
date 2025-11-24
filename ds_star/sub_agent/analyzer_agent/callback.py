import os
import subprocess
import tempfile
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
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


def after_analyzer_agent_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    state = callback_context.session.state
    filename = state.get("filename")
    executable_code = ExecutableCode.model_validate(obj=state.get("executable_code"))
    description = _run_temp_python(code=executable_code.code)

    if "data_descriptions" not in state:
        state["data_descriptions"] = {}
    state["data_descriptions"][filename] = description

    return types.Content(role="user", parts=[types.Part(text=description)])
