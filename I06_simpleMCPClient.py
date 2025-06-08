from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent

from dotenv import load_dotenv
import asyncio

load_dotenv()

# MCP server configuration
MCP_URL = "http://localhost:8000/sse"
client = BasicMCPClient(MCP_URL)
print(f"Connecting to MCP server at {MCP_URL}...")


async def main():
    # Get available tools and format it in usalble way for the agent
    tools_spec = McpToolSpec(client=client)

    tools = await asyncio.wait_for(
        tools_spec.to_tool_list_async(),
        timeout=10
    )

    # print(f"Available tools: {tools}")
    
    # To display details of the tools 
    # for tool in tools:
    #     metadata = getattr(tool, "_metadata", None)
    #     if metadata:
    #         print(f"Tool Name      : {metadata.name}")
    #         print(f"Description    : {metadata.description}")
    #         print(f"Function Schema: {metadata.fn_schema}")
    #         print(f"Return Direct? : {metadata.return_direct}")
    #         print("-" * 40)
    #         schema = metadata.fn_schema
    #         if schema:
    #             print("Input Parameters:")
    #             for field_name, field in schema.model_fields.items():
    #                 print(f"  - {field_name}: {field}")
    #     else:
    #         print("No metadata available for this tool.")
    # Now run the agent
    # agent = FunctionAgent(
    #     name="Agent",
    #     description="Some description",
    #     llm=OpenAI(model="gpt-4o-mini",verbose=True),
    #     tools=tools,
    #     system_prompt="You are a helpful assistant.",
    #     verbose=True,
    # )

    agent = OpenAIAgent.from_tools(
        tools,
        llm=OpenAI(model="gpt-4o-mini",verbose=True),
        system_prompt="You are a helpful assistant.",
        verbose=True,
    )

    # print(dir(agent)) - Available methods of the agent

    resp = await agent.achat("What is the weather in my city?")
    print(resp)

if __name__ == "__main__":
    asyncio.run(main())