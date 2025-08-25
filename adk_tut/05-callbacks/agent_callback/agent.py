"""
Define functions or steps to be executed before and after agent call. 

Here defined the time it took to execute the agent 

PS: The variable name should be callback_context.
"""


from google.adk.agents import Agent
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from typing import Optional
from datetime import datetime


def before_agent_callback(callback_context : CallbackContext) -> Optional[types.Content]:
    state = callback_context.state
    timestamp = datetime.now()

    if "agent_name" not in state:
        state['agent_name'] = 'jinu bot'

    if "request_counter" in state:
        state["request_counter"] += 1
    else:
        state["request_counter"] = 1
    
    state['request_start_time'] = timestamp

    return None

def after_agent_callback(callback_context : CallbackContext) -> Optional[types.Content]:
    state = callback_context.state
    timestamp = datetime.now()

    duration = (timestamp - state['request_start_time']).total_seconds()

    print(f"Request #: {state.get('request_counter', 'Unknown')}")
    print(f"Duration #: {duration:.2f} seconds")

    return None




root_agent = Agent(
    name="before_after_agent",
    model="gemini-2.0-flash",
    description="A basic friendly greeting agent",
    instruction="""
    You are a friendly greeting agent. Your name is {agent_name}.
    
    Your job is to:
    - Greet users politely
    - Respond to basic questions
    - Keep your responses friendly and concise
    """,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)