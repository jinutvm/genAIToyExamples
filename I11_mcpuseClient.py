import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
import base64
import json

async def main():
    """Run the example using a configuration file."""
    # Load environment variables
    load_dotenv()

    # Create configuration
    config = {
        "type": "object",
        "default": {},
        "description": "Empty configuration for MCP Domino's Pizza server"
    }

    # Encode config in base64 - exactly like the sample code
    config_b64 = base64.b64encode(json.dumps(config).encode()).decode("utf-8")

    # Create MCP client configuration
    mcp_config = {
        "mcpServers": {
            "http": {
                "url": f"https://server.smithery.ai/@mdwoicke/mcp-dominos-pizza/mcp?config={config_b64}&api_key={os.getenv('smithery_api_key')}"
            }
        }
    }

    print(f"Debug - Config URL: {mcp_config['mcpServers']['http']['url']}")
    print(f"Debug - API Keys loaded: {bool(os.getenv('smithery_api_key'))} {bool(os.getenv('OPENAI_API_KEY'))}")

    # Create MCPClient from config file
    client = MCPClient.from_dict(mcp_config)

    # Create LLM
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        api_key=os.getenv('OPENAI_API_KEY')
    )

    # Create agent with the client
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=30,
        verbose=True  # Enable verbose output to see what's happening
    )

    # Run the query
    result = await agent.run(
        "get menu for shop 7136",
        max_steps=30,
    )
    print(f"\nResult: {result}")

if __name__ == "__main__":
    asyncio.run(main())