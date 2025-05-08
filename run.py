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
import csv
from datetime import datetime
import os
import time

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
        self.csv_file = "quotes.csv"
        self.rate_limit_delay = 1  # 1 second between requests
        self.last_request_time = 0
        # Create CSV file with headers if it doesn't exist
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Quote', 'Author', 'Tags', 'Timestamp'])
    
    async def list_tools(self) -> list[Tool]:
        return [Tool(
            name="fetch_all_quotes",
            description="Fetches all quotes from quotes.toscrape.com with rate limiting",
            parameters={
                "type": "object",
                "properties": {}
            }
        )]
    
    async def save_to_csv(self, quotes):
        """Save quotes to CSV file"""
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for quote in quotes:
                writer.writerow([
                    quote['text'],
                    quote['author'],
                    ','.join(quote['tags']),
                    datetime.now().isoformat()
                ])

    async def fetch_page(self, page_num):
        """Fetch a single page with rate limiting"""
        # Implement rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last_request)
        
        url = f"https://quotes.toscrape.com/page/{page_num}/"
        logger.info(f"Fetching page {page_num}")
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            self.last_request_time = time.time()
            
            if response.status_code == 404:
                return None, True  # No more pages
            
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
            
            # Check if this is the last page
            next_button = soup.find('li', class_='next')
            is_last_page = next_button is None
            
            return quotes, is_last_page
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None, True
            raise
    
    async def call_tool(self, name: str, arguments: dict) -> list[TextContent]:
        if name == "fetch_all_quotes":
            all_quotes = []
            page_num = 1
            total_quotes = 0
            
            try:
                while True:
                    quotes, is_last_page = await self.fetch_page(page_num)
                    
                    if quotes is None or not quotes:
                        break
                    
                    # Save quotes to CSV
                    await self.save_to_csv(quotes)
                    
                    all_quotes.extend(quotes)
                    total_quotes += len(quotes)
                    
                    logger.info(f"Saved {len(quotes)} quotes from page {page_num}")
                    
                    if is_last_page:
                        break
                    
                    page_num += 1
                
                return [TextContent(
                    type="text",
                    text=f"Successfully scraped and saved {total_quotes} quotes from {page_num} pages to {self.csv_file}"
                )]
            except Exception as e:
                logger.error(f"Error fetching quotes: {str(e)}")
                return [TextContent(type="text", text=f"Error fetching quotes: {str(e)}")]
        return []

server = QuotesScraperServer()

async def fetch_all_quotes_endpoint(request):
    result = await server.call_tool("fetch_all_quotes", {})
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
    Route("/quotes", endpoint=fetch_all_quotes_endpoint)
])

if __name__ == "__main__":
    logger.info("Starting Quotes Scraper MCP Server on http://localhost:7860")
    uvicorn.run(app, host="127.0.0.1", port=7860, log_level="debug")