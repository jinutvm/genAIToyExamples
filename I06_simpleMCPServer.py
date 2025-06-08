#Create a simple MCP server
#pip install mcp llama-index llama-index-tools-mcp requests
from mcp.server.fastmcp import FastMCP
import os

# Create a simple MCP server
mcp = FastMCP("SimpleServer")


# register tools 
# @mcp.tool() decorator helps in defining the tool and its parameters in the fofmat required 

@mcp.tool()
def hello_world(name: str = "World"):
    """A simple hello world tool."""
    return {"message": f"Hello, {name}!"}

@mcp.tool()
def add(a: int, b: int):
    """Add two numbers."""
    return a + b

@mcp.tool()
def get_weather(city: str):
    """Get the weather of a city."""
    return {"weather": f"The weather of {city} is sunny."}

@mcp.tool()
def get_my_city(city: str):
    """Get the city of the user"""
    return {"city": f"The city is Kochi"}




if __name__ == "__main__":
    print("Starting MCP server on default port...")
    mcp.run("sse")