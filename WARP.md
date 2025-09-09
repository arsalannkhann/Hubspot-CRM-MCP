# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This repository contains two MCP (Model Context Protocol) servers:

1. **HubSpot CRM MCP Server** (`hubspot_mcp.py`) - Specialized server for HubSpot CRM operations
2. **Business Tools MCP Server** (`business_tools_mcp.py`) - Comprehensive server with 10 business tools, LLM-agnostic design

Both servers implement the MCP protocol to expose functionality as tools that can be consumed by any MCP-compatible client, including LLMs like Gemini, Llama 3, Claude, or GPT.

## Architecture

### Dual Server Architecture

The repository supports two independent MCP servers:
- **Focused Server**: `hubspot_mcp.py` for HubSpot-specific operations
- **Comprehensive Server**: `business_tools_mcp.py` for multiple business integrations
- **LLM Flexibility**: `llm_client.py` provides LLM-agnostic interface for AI integration

### Core Components

- **MCP Protocol Layer** - Handles tool registration, validation, and async execution
- **Configuration Management** - `config.py` centralizes all API keys and settings
- **LLM Client Helper** - `llm_client.py` enables switching between different LLM providers
- **Environment Management** - Uses `python-dotenv` for secure credential handling

### Business Tools MCP Server Architecture

The business tools server provides 10 modular tools:
1. **Web Search** - SerpAPI/Google Custom Search (fully implemented)
2. **Database Query** - SQLAlchemy for Postgres/MySQL/SQLite (stubbed)
3. **CRM Operations** - HubSpot & Salesforce integration (stubbed)
4. **Data Enrichment** - Clearbit & People Data Labs (stubbed)
5. **Calendar Management** - Google Calendar & Outlook (stubbed)
6. **Twilio Communication** - SMS, Voice, WhatsApp (stubbed)
7. **Email Services** - SendGrid & Mailgun (stubbed)
8. **Stripe Payments** - Payments, subscriptions, invoicing (stubbed)
9. **Docs/Knowledge Base** - Notion & Google Drive (stubbed)
10. **Social Media** - LinkedIn & Twitter/X posting (stubbed)

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python3 -m venv business-env
source business-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Running the Servers

#### HubSpot CRM Server
```bash
# Using the launcher script
./run_server.sh

# Manual execution
source hubspot-env/bin/activate
python hubspot_mcp.py
```

#### Business Tools Server
```bash
source business-env/bin/activate
python business_tools_mcp.py
```

### Testing Commands
```bash
# Test HubSpot MCP server
python test_simple.py

# Test API connections
python test_connection.py

# Test LLM providers
python llm_client.py

# Validate configuration
python config.py
```

### MCP Client Configuration

#### For HubSpot CRM Server
```json
{
  "mcpServers": {
    "hubspot-crm": {
      "command": "/path/to/hubspot-env/bin/python",
      "args": ["/path/to/hubspot_mcp.py"]
    }
  }
}
```

#### For Business Tools Server
```json
{
  "mcpServers": {
    "business-tools": {
      "command": "/path/to/business-env/bin/python",
      "args": ["/path/to/business_tools_mcp.py"]
    }
  }
}
```

## LLM Integration

### Switching LLM Providers

The system supports multiple LLM providers through the `llm_client.py` module:

```python
from llm_client import LLMClient, query_llm

# Use default provider from config
response = query_llm("Your prompt here")

# Switch providers dynamically
client = LLMClient(provider="gemini")  # or "llama3", "openai", "claude"
response = await client.query("Your prompt here")
```

### Supported LLM Providers
- **Gemini** - Google's Gemini models
- **Llama3** - Local fine-tuned Llama 3 via Ollama
- **OpenAI** - GPT-3.5/GPT-4 models
- **Claude** - Anthropic's Claude models
- **Mock** - Testing fallback

## API Requirements

### HubSpot CRM Server
- `crm.objects.contacts` (read & write)
- `crm.objects.deals` (read & write)
- `crm.schemas.deals` (read & write)

### Business Tools Server
See `.env.example` for complete list of required API keys for each tool.

## Key Implementation Details

### Async Architecture
- Both servers run on `mcp.server.stdio` with async I/O streams
- All tool handlers are async functions returning `list[types.TextContent]`
- Uses `asyncio.run(main())` for server execution

### Error Handling Strategy
- Structured JSON error responses: `{"error": "message", "tool": "tool_name"}`
- Graceful fallbacks when API keys are not configured
- Mock responses available for testing without API keys

### LLM-Agnostic Design
- MCP servers don't depend on any specific LLM
- Tools return JSON-serializable dictionaries
- LLM logic completely separated from MCP server logic
- Easy to swap between different LLM providers via configuration

## File Structure

### MCP Servers
- **`hubspot_mcp.py`** - HubSpot-specific MCP server
- **`business_tools_mcp.py`** - Multi-tool business MCP server
- **`config.py`** - Centralized configuration management
- **`llm_client.py`** - LLM provider abstraction layer

### Testing & Demos
- **`test_simple.py`** - MCP server test script
- **`test_connection.py`** - API connection tester
- **`test_mcp_server.py`** - Protocol compliance tests
- **`demo.py`** - Direct API usage examples

### Configuration
- **`.env`** - Your actual API keys (create from .env.example)
- **`.env.example`** - Template for environment variables
- **`requirements.txt`** - Python dependencies
- **`mcp_config.json`** - MCP client configuration example

### Legacy/Backup
- **`hubspot_mcp_server_fixed.py`** - Previous server implementation
- **`old_demo_mcp.py`** - Deprecated demo script

## Development Workflow

### Adding New Tools to Business Server
1. Add tool definition in `handle_list_tools()`
2. Create async handler function following naming pattern `{tool_name}_tool()`
3. Add routing in `handle_call_tool()`
4. Add required API keys to `config.py` and `.env.example`
5. Update `requirements.txt` with needed libraries

### Testing Individual Tools
```python
# Test a specific tool directly
import asyncio
from business_tools_mcp import web_search_tool

result = asyncio.run(web_search_tool({"query": "test search"}))
print(result)
```

## Production Deployment

### Containerization
Both servers are ready for containerization:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "business_tools_mcp.py"]
```

### Environment Variables
Always use environment variables for sensitive data:
- Never commit `.env` files
- Use secret management services in production
- Rotate API keys regularly

### Scaling Considerations
- Each MCP server runs independently
- Can deploy servers separately based on needs
- Stateless design allows horizontal scaling
- Consider rate limiting for external API calls
