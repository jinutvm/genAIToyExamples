from google.adk.agents import Agent


"""
Simple agent which can help answer queries 

need to define in env file
GOOGLE_API_KEY='*****'

01-test1 
    basic_agent
        __init__.py
        basicagent.py

How to Run
1. There is an sdk which will help us to run this agent for testing purposes. 
    - in the above folder structure open 01-test1 and then type "adk web"
    - This will open a web based tool where you can test this application 
Things to ensure 
    - If possible instead of basicagent.py, rename as agent.py
    - Agent defined should be always assigned to root_agent
    - When you type "adk web" at "01-test01" level it will search for <folder-name(basic_agent in this case)>.agent.root_agent and will be invoked
    - If we need to rename agent.py then ensure the __init__.py is exposing root_agent  
"""


root_agent = Agent(
    name="helpful_agent", # name should not have spaces and can have only letters, numbers and _
    model="gemini-2.0-flash",
    description="Agent helping user queries",
    instruction="""
    You are a helpful assistant that helps resolve the user queries. 
    """,
)