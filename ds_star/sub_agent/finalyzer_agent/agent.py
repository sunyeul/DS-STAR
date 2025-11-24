from google.adk.agents import Agent

from .callbacks import finalyzer_before_model_callback

finalyzer_agent = Agent(
    model="gemini-2.5-flash",
    name="finalyzer_agent",
    description="A finalyzer agent that finalizes the answer to the question.",
    instruction="""
You are an expert data analysist.
You will answer factoid question by loading and referencing the files/documents listed below.
You also have a reference code.
Your task is to make solution code to print out the answer of the question following the given guideline.
""",
    output_key="final_answer",
    before_model_callback=finalyzer_before_model_callback,
)
