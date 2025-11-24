from google.adk.agents import LlmAgent

from config import PathsConfig

from .callback import after_analyzer_agent_callback
from .models import ExecutableCode

paths_config = PathsConfig()

# Agent Definition
analyzer_agent = LlmAgent(
    name="analyzer_agent",
    model="gemini-2.5-flash",
    instruction="""
You are an expert data analysist.
Generate a Python code that loads and describes the content of {filename}.

# Requirement
- The file can both unstructured or structured data.
- If there are too many structured data, print out just few examples.
- Print out essential informations. For example, print out all the column names.
- The Python code should print out the content of {filename}.
- The code should be a single-file Python program that is self-contained and can be executed as-is.
- Your response should only contain a single code block.
- Important: You should not include dummy contents since we will debug if error occurs.
- Do not use try: and except: to prevent error. I will debug it later.
    """,
    description="Analyzes the content of a file and generates a Python code to describe the content.",
    output_key="executable_code",
    output_schema=ExecutableCode,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    after_agent_callback=after_analyzer_agent_callback,
)
