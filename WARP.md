# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This is a production-ready **Model Context Protocol (MCP) server** that provides structured JSON APIs for business automation tools. The server follows a modular architecture with clean separation between LLM logic and server implementation, supporting multiple LLM providers and exposing 10 comprehensive business tools.

## Core Architecture

### Server Architecture
- **MCP Protocol Layer**: Handles JSON-RPC communication via stdio
- **Tool Layer**: 10 business tools with standardized JSON input/output
- **LLM Configuration Layer**: Multi-provider support (OpenAI, Anthropic, Google Gemini, local models)
- **API Integration Layer**: Direct connections to business service APIs
- **Async Processing**: Built on asyncio for concurrent request handling

### Key Design Principles
- **Modular**: Each tool is self-contained with clear interfaces
- **Configurable**: Environment-based configuration with fallback defaults
- **Error-Resilient**: Comprehensive error handling with graceful degradation
- **Production-Ready**: Includes logging, connection pooling, and graceful shutdown

## Common Development Commands

### Server Operations
```bash
# Start the MCP server
python3 business_tools_mcp.py

# Run comprehensive tool tests
python3 test_all_tools.py

# Run MCP protocol tests
python3 test_mcp_server.py

# Validate configuration
python3 -c "from config import validate_configuration; validate_configuration()"
```

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit configuration
# Configure API keys in .env file for tools you want to test
```

### Testing Individual Tools
```bash
# Test specific MCP tool via JSON-RPC
python3 test_mcp_simple.py

# Check server startup without full initialization
python3 business_tools_mcp.py &
PID=$!; sleep 2; kill $PID
```

## Available Business Tools

The server provides 10 comprehensive business tools:

1. **web_search** - SerpAPI/Google Custom Search integration
2. **database_query** - MongoDB/SQL database operations with full CRUD support
3. **crm_operation** - HubSpot/Salesforce CRM management
4. **enrich_data** - Clearbit/People Data Labs data enrichment
5. **calendar_operation** - Google Calendar/Outlook integration
6. **twilio_communication** - SMS/WhatsApp/Voice via Twilio
7. **send_email** - SendGrid/Mailgun/Gmail SMTP
8. **stripe_operation** - Payment processing and subscription management
9. **docs_operation** - Notion/Google Drive document management
10. **social_media_post** - Twitter/X posting with dry-run support

## Configuration Architecture

### Environment Variables
Configuration is centralized in `config.py` with environment variable support:
- **LLM Providers**: OPENAI_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY
- **Business APIs**: Tool-specific tokens (HUBSPOT_TOKEN, STRIPE_KEY, etc.)
- **Server Settings**: MCP_SERVER_PORT, MCP_LOG_LEVEL, rate limiting

### Dynamic Tool Loading
The `get_configured_tools()` function automatically detects which tools are available based on configured API keys, enabling graceful degradation when services are unavailable.

## Code Organization

### Main Server File
- `business_tools_mcp.py` - Main MCP server with all 10 tools implemented inline
- JSON-RPC request routing with comprehensive error handling
- Async client initialization with connection reuse

### Configuration Management
- `config.py` - Centralized configuration with validation
- `.env.example` - Template with all supported environment variables
- Dynamic API key detection and tool availability checking

### Testing Framework
- `test_all_tools.py` - Comprehensive test suite for all 10 tools
- `test_mcp_server.py` - MCP protocol compliance testing
- JSON-RPC request/response validation with timeout handling

## MCP Integration

### Claude Desktop Integration
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "business-tools": {
      "command": "python3",
      "args": ["/path/to/business_tools_mcp.py"],
      "env": {
        "PYTHONPATH": "/path/to/Hubspot-CRM-MCP"
      }
    }
  }
}
```

### MCP Protocol Details
- **Transport**: stdio (standard input/output)
- **Format**: JSON-RPC 2.0
- **Tool Schema**: Standardized input validation via JSON Schema
- **Response Format**: TextContent with JSON payloads

## Development Guidelines

### Adding New Tools
1. Define tool schema in `handle_list_tools()` with proper JSON Schema validation
2. Implement async tool function following the pattern: `async def {tool_name}_tool(args: Dict[str, Any]) -> List[types.TextContent]`
3. Add tool routing in `handle_call_tool()`
4. Update configuration detection in `get_configured_tools()`
5. Add comprehensive tests in `test_all_tools.py`

### Error Handling Pattern
All tools follow consistent error handling:
```python
try:
    # Tool implementation
    return [types.TextContent(type="text", text=json.dumps({
        "success": True,
        "data": result_data
    }))]
except Exception as e:
    logger.error(f"Tool failed: {e}")
    return [types.TextContent(type="text", text=json.dumps({
        "error": f"Tool execution failed: {str(e)}",
        "tool": "tool_name"
    }))]
```

### Database Operations
The MongoDB support includes full CRUD operations:
- **Find**: Flexible querying with projection, sorting, pagination
- **Insert**: Single/batch document insertion
- **Update**: Targeted updates with upsert support
- **Delete**: Single/bulk deletion
- **Aggregate**: Pipeline-based data processing
- **Count/Distinct**: Analytics operations

## Production Deployment

### Service Configuration
The server is designed for production deployment with:
- Graceful shutdown handling (SIGTERM/SIGINT)
- Connection cleanup for database/HTTP clients
- Comprehensive logging with configurable levels
- Rate limiting and authentication support (configurable)

### Scaling Considerations
- **Async Architecture**: Built for concurrent request handling
- **Connection Pooling**: Reuses database and HTTP connections
- **Stateless Design**: No server-side session management
- **Resource Management**: Proper cleanup of async resources

## Tool-Specific Development Notes

### MongoDB Integration
Full MongoDB operations with enhanced error handling, support for complex queries, aggregation pipelines, and automatic ObjectId serialization.

### HubSpot CRM
Comprehensive CRM operations including contact search by email, deal creation, and robust error handling for invalid contact IDs.

### Twitter/X Integration
Uses Twitter API v2 with bearer token authentication, includes character limit validation, and dry-run mode for testing.

### Email Services
Multi-provider support (SendGrid, Gmail SMTP, Mailgun) with HTML content detection and proper MIME handling.

### Testing Philosophy
Each tool includes both positive and negative test cases, validates error conditions, and tests configuration validation to ensure robust operation.
