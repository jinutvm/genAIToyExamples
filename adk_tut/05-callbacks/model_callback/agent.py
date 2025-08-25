"""
Define functions or steps to be executed before and after model call. 

Checks whether inappropriate content is shared with model. Also could rephrase output comning

PS: The variable name should be callback_context.
"""


from google.adk.agents import Agent
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from typing import Optional
from datetime import datetime


def before_model_callback(callback_context : CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    state = callback_context.state
    timestamp = datetime.now()

    if "agent_name" not in state:
        state['agent_name'] = 'jinu bot'

    if "request_counter" in state:
        state["request_counter"] += 1
    else:
        state["request_counter"] = 1
    

    last_user_message = ""
    if llm_request.contents and len(llm_request.contents) > 0:
        for content in reversed(llm_request.contents):
            if content.role == "user" and content.parts and len(content.parts) > 0:
                if hasattr(content.parts[0], "text") and content.parts[0].text:
                    last_user_message = content.parts[0].text
                    state["last_user_message"] = last_user_message
                    break

    if "sucks" in last_user_message.lower():
        # Return a response to skip the model call
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text="I cannot respond to messages containing inappropriate language. "
                        "Please rephrase your request without using words like 'sucks'."
                    )
                ],
            )
        )

    state['model_start_time'] = timestamp


    return None

def after_model_callback(callback_context : CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    state = callback_context.state
    timestamp = datetime.now()

    duration = (timestamp - state['model_start_time']).total_seconds()

    print(f"Request #: {state.get('request_counter', 'Unknown')}")
    print(f"Duration #: {duration:.2f} seconds")

    return None




root_agent = Agent(
    name="before_after_agent",
    model="gemini-2.0-flash",
    description="A basic friendly greeting agent",
    instruction="""
    You are a friendly greeting agent.
    
    Your job is to:
    - Greet users politely
    - Respond to basic questions
    - Keep your responses friendly and concise
    """,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)