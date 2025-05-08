# MCP Quotes Scraper Project Documentation

## 1. Project Overview
This project implements a web scraping service using the Model Context Protocol (MCP) framework to extract quotes from quotes.toscrape.com. The service provides real-time quote data through HTTP endpoints and uses Server-Sent Events (SSE) for live updates.

## 2. Technical Stack
- **Primary Language**: Python
- **Key Libraries**:
  - MCP (Model Context Protocol) - For server implementation
  - Starlette - ASGI web framework
  - Uvicorn - ASGI server implementation
  - BeautifulSoup4 - For HTML parsing
  - httpx - For making HTTP requests
  - SSE-Starlette - For Server-Sent Events

## 3. Project Structure
```
MCP/
├── run.py                 # Main server implementation
├── README.md             # Project documentation
├── mcp_server.log        # Server logs
└── my_env_folder/        # Python virtual environment
    └── env/              # Contains all dependencies
```

## 4. Implementation Details

### 4.1 Server Architecture
The server is implemented as a `QuotesScraperServer` class that inherits from `mcp.server.lowlevel.Server`. Key features include:
- Server-Sent Events (SSE) for real-time updates
- RESTful endpoints for quote retrieval
- Structured quote data extraction
- Asynchronous HTTP client for efficient web scraping

### 4.2 Available Endpoints

1. Root Endpoint ('/')
   - Provides SSE connection
   - Sends initialization events
   - Maintains connection alive

2. Quotes Endpoint ('/quotes')
   - Accepts page parameter for pagination
   - Returns structured quote data
   - Example: http://localhost:7860/quotes?page=2

### 4.3 Data Format
The server returns quotes in the following JSON structure:
```json
{
    "result": [{
        "type": "text",
        "text": "Quotes from page X:\n\nQuote: [quote text]\nAuthor: [author name]\nTags: [tag1, tag2, ...]"
    }]
}
```

## 5. Setup and Installation

### 5.1 Prerequisites
- Python 3.8 or higher
- Virtual environment (included in my_env_folder)

### 5.2 Dependencies
All required packages are installed in the virtual environment:
- mcp-server-fetch
- httpx
- beautifulsoup4
- starlette
- uvicorn

### 5.3 Running the Server
1. Activate the virtual environment:
   ```bash
   cd MCP
   .\my_env_folder\env\Scripts\activate
   ```

2. Start the server:
   ```bash
   python run.py
   ```

3. The server will run on http://localhost:7860

## 6. Features

### 6.1 Quote Scraping
- Extracts quotes from quotes.toscrape.com
- Includes quote text, author, and tags
- Supports pagination
- Clean and formatted output

### 6.2 Real-time Updates
- SSE implementation for live data
- Continuous connection maintenance
- Regular initialization events
- Efficient async operations

### 6.3 Error Handling
- Comprehensive error handling for HTTP requests
- Proper error messages for failed scraping attempts
- Logging of all operations

## 7. Usage Examples

### 7.1 Getting Quotes
1. View first page of quotes:
   ```
   GET http://localhost:7860/quotes
   ```

2. Access specific page:
   ```
   GET http://localhost:7860/quotes?page=2
   ```

### 7.2 Monitoring
- Check server logs in mcp_server.log
- Watch terminal output for real-time debugging
- Monitor SSE events through browser developer tools

## 8. Best Practices Implemented

### 8.1 Code Organization
- Clear class structure
- Separation of concerns
- Modular design
- Proper error handling

### 8.2 Performance
- Async HTTP client for efficient requests
- Clean HTML parsing with BeautifulSoup4
- Resource cleanup and management

## 9. Future Enhancements
Potential improvements could include:
1. Caching mechanism for frequently accessed quotes
2. Rate limiting implementation
3. Additional endpoints for:
   - Author-specific quotes
   - Tag-based filtering
   - Random quote selection

## 10. Troubleshooting

### Common Issues
1. Server won't start
   - Check if port 7860 is available
   - Verify virtual environment is activated
   - Ensure all dependencies are installed

2. No quotes displayed
   - Verify internet connection
   - Check if quotes.toscrape.com is accessible
   - Look for errors in server logs

### Support
For issues and contributions, please refer to the project documentation or raise an issue in the repository.

## 11. License
This project is open-source and available under the MIT License.

---
Last updated: May 8, 2025