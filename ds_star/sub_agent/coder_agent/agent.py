from google.adk.agents import Agent

from config import PathsConfig

from .callbacks import (
    after_coder_agent_callback,
    coder_before_model_callback,
    initial_coder_before_model_callback,
)
from .models import ExecutableCode

paths_config = PathsConfig()


initial_coder_agent = Agent(
    model="gemini-2.5-flash",
    name="initial_coder_agent",
    description="An initial coder agent that codes the first step to answer the question.",
    output_key="base_code",
    output_schema=ExecutableCode,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    before_model_callback=initial_coder_before_model_callback,
    after_agent_callback=after_coder_agent_callback,
)


coder_agent = Agent(
    model="gemini-2.5-flash",
    name="coder_agent",
    description="A coder agent that codes the next step to answer the question.",
    instruction="""
You are an expert data analysist.
Your task is to implement the current plan with the given data.
""",
    output_key="base_code",
    output_schema=ExecutableCode,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    before_model_callback=coder_before_model_callback,
    after_agent_callback=after_coder_agent_callback,
)
