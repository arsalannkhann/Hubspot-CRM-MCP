# Business Tools MCP Server

A modular Model Context Protocol (MCP) server that provides LLM-powered tools for business automation, supporting multiple LLM providers and exposing clean JSON APIs for various business tools integration.

## Features

- **Modular Architecture**: Clean separation between LLM logic and server implementation
- **Multi-Provider Support**: Configure multiple LLM providers (OpenAI, Anthropic, Google Gemini) via configuration file
- **Business Tool Integration**: Extensible framework for adding business automation tools
- **MCP Protocol**: Full support for Model Context Protocol standards

## Project Structure

```
business_tools_mcp/
├── business_tools_mcp/       # Main package directory
│   ├── __init__.py
│   ├── config/               # Configuration management
│   │   └── __init__.py
│   └── tools/                # Business tools implementations
│       └── __init__.py
├── tests/                    # Test suite
│   └── __init__.py
├── business_tools_mcp.py     # Main MCP server entry point
├── config.py                 # Configuration loader
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/business-tools-mcp.git
cd business-tools-mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Configuration

The server supports configuration through:
- Environment variables (`.env` file)
- Configuration file (`config.py`)
- Runtime parameters

### Environment Variables

```bash
# LLM Provider API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Business Tool API Keys
HUBSPOT_ACCESS_TOKEN=your_hubspot_token
JINA_API_KEY=your_jina_key
GOOGLE_CREDENTIALS_PATH=/path/to/google/credentials.json

# Default LLM Provider
DEFAULT_LLM_PROVIDER=openai

# Server Configuration
MCP_SERVER_PORT=3000
MCP_SERVER_HOST=localhost
```

## Usage

### Starting the Server

```bash
python business_tools_mcp.py
```

### Using with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "business-tools": {
      "command": "python",
      "args": ["/path/to/business_tools_mcp.py"],
      "env": {
        "OPENAI_API_KEY": "your_key_here",
        "HUBSPOT_ACCESS_TOKEN": "your_token"
      }
    }
  }
}
```

## Available Tools

### CRM Tools
- `crm_create` - Create contacts, companies, deals, or tasks
- `crm_get` - Retrieve CRM records
- `crm_update` - Update existing records
- `crm_list` - List records with filters
- `crm_delete` - Delete records

### Social Media Tools
- `social_media_post` - Create posts on supported platforms

### Documentation Tools
- `docs_create` - Create documents
- `docs_append` - Append content to existing documents

### Web Scraping Tools
- `scrape_webpage` - Extract content from web pages

## Development

### Adding New Tools

1. Create a new tool module in `business_tools_mcp/tools/`
2. Implement the tool interface
3. Register the tool in the main server

### Running Tests

```bash
python -m pytest tests/
```

## Architecture

The server follows a modular architecture with clear separation of concerns:

- **MCP Server Layer**: Handles protocol communication and request routing
- **Tool Layer**: Implements business logic for various tools
- **LLM Layer**: Manages interactions with different LLM providers
- **Config Layer**: Handles configuration and environment management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.
