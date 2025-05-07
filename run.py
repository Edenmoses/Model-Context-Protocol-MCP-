from mcp.server.lowlevel import Server
from mcp.server.models import InitializationOptions
from mcp.types import TextContent, Tool
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from sse_starlette.sse import EventSourceResponse
import asyncio
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("mcp-server")

class EchoServer(Server):
    def __init__(self):
        super().__init__(name="echo-server")
    
    async def list_tools(self) -> list[Tool]:
        return [Tool(
            name="echo",
            description="Echoes back the message sent by the user",
            parameters={
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"]
            }
        )]
    
    async def call_tool(self, name: str, arguments: dict) -> list[TextContent]:
        if name == "echo":
            message = arguments.get("message", "")
            logger.info(f"Echoing message: {message}")
            return [TextContent(type="text", text=f"You said: {message}")]
        return []

server = EchoServer()

async def sse_endpoint(request):
    async def event_generator():
        while True:
            # Send initialization
            yield {
                "data": server.create_initialization_options().json(),
                "event": "initialize"
            }
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())

app = Starlette(debug=True, routes=[
    Route("/", endpoint=sse_endpoint)
])

if __name__ == "__main__":
    logger.info("Starting MCP SSE Server on http://localhost:7860")
    uvicorn.run(app, host="127.0.0.1", port=7860, log_level="debug")