#  Self Hosted MCP serverStarts the I07_math_server.py and uses the tools to answer questions. 
# Create agent will ensure the tools are called in the right order."


from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
import asyncio
from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv

load_dotenv()

model = ChatAnthropic(
    model="claude-opus-4-20250514",  # or claude-3-opus, haiku, etc.
    temperature=0.7,
    api_key=os.getenv("ANTHROPIC_API_KEY")  # or hardcode if testing
)

server_params = StdioServerParameters(
    command="python",
    args=[
        "/Users/jinubabu/Documents/Cosmaya/genAIToyExamples/I07math_server.py"
      ]
)

async def run_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)
            print("Loaded tools:", [t.name for t in tools])
            # Create and run the agent
            agent = create_react_agent(model, tools)
            agent_response = await agent.ainvoke({"messages": "what is (2+3)x4"})
            print(agent_response)
            return agent_response

# Run the async function
if __name__ == "__main__":
    try:
        result = asyncio.run(run_agent())
        print(result)
    except Exception as e:
        import traceback
        traceback.print_exc()