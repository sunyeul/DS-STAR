from google.adk.agents import Agent

from .callbacks import (
    append_plan,
    initial_planner_before_model_callback,
    planner_before_model_callback,
)

initial_planner_agent = Agent(
    model="gemini-2.5-flash",
    name="initial_planner_agent",
    description="An initial planner agent that plans the first step to answer the question.",
    instruction="""
You are an expert data analysist.
In order to answer factoid questions based on the given data, you have to first plan effectively.
    """,
    output_key="current_plan",
    before_model_callback=initial_planner_before_model_callback,
    after_agent_callback=append_plan,
)

planner_agent = Agent(
    model="gemini-2.5-flash",
    name="planner_agent",
    description="A planner agent that plans the next step to answer the question.",
    instruction="""
You are an expert data analysist.
In order to answer factoid questions based on the given data, you have to first plan effectively.
Your task is to suggest next plan to do to answer the question.
""",
    output_key="current_plan",
    before_model_callback=planner_before_model_callback,
    after_agent_callback=append_plan,
)
