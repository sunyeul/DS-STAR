from google.adk.agents import Agent

from .callbacks import router_before_model_callback
from .models import RouterOutput

router_agent = Agent(
    model="gemini-2.5-flash",
    name="router_agent",
    description="A router agent that routes the question to the appropriate agent.",
    instruction="""
You are an expert data analysist.
Since current plan is insufficient to answer the question, your task is to decide how to refine the plan to answer the question.
""",
    output_key="router_output",
    output_schema=RouterOutput,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    before_model_callback=router_before_model_callback,
)
