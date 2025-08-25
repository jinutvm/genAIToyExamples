"""
Define functions or steps to be executed before and after tool call.

Have provided constraints to the tool input. For calculate tool check whether first digit is positive.

PS: The state will be on tool_context here.
"""

from google.adk.agents import Agent
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from typing import Optional
from datetime import datetime
import time
from google.adk.tools.base_tool import BaseTool
from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext


def before_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[types.Content]:
    tool_name = tool.name
    timestamp = datetime.now()
    
    # Track tool usage

    if tool_name == "calculate_sum" and not args.get("a",0) >=0:
        return {"result": "Variable 'a' should always postive"}
    
    state = tool_context.state
    state['tool_start_time'] = timestamp

    return None


def after_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict) -> Optional[Dict]:
    
    state = tool_context.state
    timestamp = datetime.now()
    
    

    duration = (timestamp - state['tool_start_time']).total_seconds()
    print(f"Tool completed in {duration:.2f} seconds")
    print(f"Tool response can also be edited  {tool_response}" )
    
    return None


def calculate_sum(a: int, b: int) -> int:
    """A simple tool that adds two numbers together."""
    # Add a small delay to make the timing visible
    time.sleep(0.5)
    result = a + b
    print(f"Calculating: {a} + {b} = {result}")
    return result


def get_current_time() -> str:
    """A simple tool that returns the current time."""
    time.sleep(0.2)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Current time: {current_time}")
    return current_time


root_agent = Agent(
    name="tool_callback_demo",
    model="gemini-2.0-flash",
    description="A demo agent with tool callbacks",
    instruction="""
    You are a helpful assistant that can use tools.
    
    Your job is to:
    - Answer questions using available tools
    - Demonstrate tool callback functionality
    - Keep responses helpful and concise
    
    You have access to these tools:
    - calculate_sum: Add two numbers together
    - get_current_time: Get the current date and time
    """,
    tools=[calculate_sum, get_current_time],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)