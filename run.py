from mcp.server.lowlevel import Server
from mcp.server.models import InitializationOptions
from mcp.types import TextContent, Tool
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
import asyncio
import logging
import sys
import httpx
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("mcp-server")

class QuotesScraperServer(Server):
    def __init__(self):
        super().__init__(name="quotes-scraper-server")
        self.client = httpx.AsyncClient()
    
    async def list_tools(self) -> list[Tool]:
        return [Tool(
            name="fetch_quotes",
            description="Fetches quotes from quotes.toscrape.com",
            parameters={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "Page number to fetch (optional)"}
                }
            }
        )]
    
    async def call_tool(self, name: str, arguments: dict) -> list[TextContent]:
        if name == "fetch_quotes":
            page = arguments.get("page", 1)
            url = f"https://quotes.toscrape.com/page/{page}/"
            try:
                logger.info(f"Fetching quotes from page {page}")
                response = await self.client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                quotes = []
                
                for quote in soup.find_all('div', class_='quote'):
                    text = quote.find('span', class_='text').get_text()
                    author = quote.find('small', class_='author').get_text()
                    tags = [tag.get_text() for tag in quote.find_all('a', class_='tag')]
                    
                    quotes.append({
                        'text': text,
                        'author': author,
                        'tags': tags
                    })
                
                formatted_quotes = "\n\n".join([
                    f"Quote: {q['text']}\nAuthor: {q['author']}\nTags: {', '.join(q['tags'])}"
                    for q in quotes
                ])
                
                return [TextContent(
                    type="text", 
                    text=f"Quotes from page {page}:\n\n{formatted_quotes}"
                )]
            except Exception as e:
                logger.error(f"Error fetching quotes: {str(e)}")
                return [TextContent(type="text", text=f"Error fetching quotes: {str(e)}")]
        return []

server = QuotesScraperServer()

async def fetch_quotes_endpoint(request):
    page = int(request.query_params.get('page', 1))
    result = await server.call_tool("fetch_quotes", {"page": page})
    return JSONResponse({"result": [r.dict() for r in result]})

async def sse_endpoint(request):
    async def event_generator():
        while True:
            yield {
                "data": server.create_initialization_options().json(),
                "event": "initialize"
            }
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())

app = Starlette(debug=True, routes=[
    Route("/", endpoint=sse_endpoint),
    Route("/quotes", endpoint=fetch_quotes_endpoint)
])

if __name__ == "__main__":
    logger.info("Starting Quotes Scraper MCP Server on http://localhost:7860")
    uvicorn.run(app, host="127.0.0.1", port=7860, log_level="debug")