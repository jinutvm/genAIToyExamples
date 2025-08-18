# Simple one 
"""
- uv init . 
- uv add fastmcp dotenv stytch sqlalchemy
- uv run main.py

Test using 
- npx @modelcontextprotocol/inspector http://127.0.0.1:8000/mcp

Install ngrok 
- Download
- Unzip    : sudo unzip ~/Downloads/ngrok-v3-stable-darwin-arm64.zip -d /usr/local/bin
- Add Auth : ngrok config add-authtoken 31QCDoZlCo9WlAOXwhHyA4iBk4H_2nPSfWofctCR6VPKMVCJf
- Free static link : ngrok http --url=thorough-bug-valid.ngrok-free.app 8000

Test using inspector 
Link - https://thorough-bug-valid.ngrok-free.app/mcp 

Testing using claude code 
Add MCP server  - claude mcp add --transport http simpletool https://thorough-bug-valid.ngrok-free.app/mcp
Exit claude     - /exit 
Restart Claude  - claude 
Check the mcp servers - /mcp 

Ask a question and it is connected. 

"""


from fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
import time


load_dotenv()


mcp = FastMCP("Simple tool")

@mcp.tool()
async def get_current_time() -> str:
    """Get the current time in a human-readable format."""
    return f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}"

@mcp.tool()
async def echo_message(message: str) -> str:
    """Echo back the provided message.
    
    Args:
        message: The message to echo back
    """
    return f"Echo: {message}"

if __name__ == "__main__":
    mcp.run(
        transport='http',
        host='127.0.0.1',
        port=8000,
        middleware = [
            Middleware(
                CORSMiddleware,
                allow_origins=['*'],
                allow_credentials=True,
                allow_methods=['*'],
                allow_headers=['*'],
            )
        ]


    )