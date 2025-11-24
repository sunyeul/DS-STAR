from google.adk.agents import Agent

from .callbacks import after_verifier_agent_callback, verifier_before_model_callback
from .models import IsEnough

verifier_agent = Agent(
    model="gemini-2.5-flash",
    name="verifier_agent",
    description="A verifier agent that verifies whether the current plan and its code implementation is enough to answer the question.",
    instruction="""
You are an expert data analysist.
Your task is to check whether the current plan and its code implementation is enough to answer the question.
""",
    output_key="is_enough",
    output_schema=IsEnough,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    before_model_callback=verifier_before_model_callback,
    after_agent_callback=after_verifier_agent_callback,
)
