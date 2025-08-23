from google.adk.agents import Agent

from preferencesagent import preference_managing_agent
from notesagent import notes_agent

root_agent = Agent(
    name="manager",
    model="gemini-2.0-flash",
    description="Manager agent",
    instruction="""
    You are a manager agent that is responsible for overseeing the work of the other agents.

    Always delegate the task to the appropriate agent. Use your best judgement 
    to determine which agent to delegate to.

    You are responsible for delegating tasks to the following agent:
    - preference_managing_agent
    - notes_agent

    If you cannot delegate tasks to any of the subagents, respond back in a professional tone to the user
    """,
    sub_agents=[preference_managing_agent,notes_agent]
)