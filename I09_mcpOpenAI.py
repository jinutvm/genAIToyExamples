# Connecting with the other MCP servers using streamablehttp_client
# Loads the tools using  load_mcp_tools which could give in the format required by langchain
# Finally uses create_react_agent to create the agent and invoke the agent to get the response from the question

import mcp
from mcp.client.streamable_http import streamablehttp_client
import json
import base64
import os
from dotenv import load_dotenv
load_dotenv()
from openai import AsyncOpenAI

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_mcp_adapters.tools import load_mcp_tools


model = ChatAnthropic(
    model="claude-opus-4-20250514",  # or claude-3-opus, haiku, etc.
    temperature=0.7,
    api_key=os.getenv("ANTHROPIC_API_KEY")  # or hardcode if testing
)



config = {
  "type": "object",
  "default": {},
  "description": "Empty configuration for MCP Domino's Pizza server"
}
# Encode config in base64
config_b64 = base64.b64encode(json.dumps(config).encode())


# Create server URL
url = f"https://server.smithery.ai/@mdwoicke/mcp-dominos-pizza/mcp?config={config_b64}&api_key={os.getenv('smithery_api_key')}"

async def main():
    # Connect to the server using HTTP client
    async with streamablehttp_client(url) as (read_stream, write_stream, _):
        async with mcp.ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()
            # List available tools
            tools_result = await session.list_tools()
            print("From List Tools: ", tools_result)
            # tools_result = await load_mcp_tools(session)
            # print("From Load MCP Tools: ", tools_result)
            # print(f"Available tools: {', '.join([t.name for t in tools_result])}")
            tools_result_openai = []
            for tool in tools_result.tools:
                tools_result_openai.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })


            agent_response = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Get me menu for store 7136"}],
                tools=tools_result_openai
            )
            print(agent_response)
            return agent_response

if __name__ == "__main__":
    import asyncio
    response = asyncio.run(main())

    print("--------------------------------")
    print("--------------------------------")
    print("--------------------------------")
    print("--------------------------------")
    print("--------------------------------")
    print("--------------------------------")
    print("Final Response: ", response['messages'][-1].content)