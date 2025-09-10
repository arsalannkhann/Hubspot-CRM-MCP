# 🚀 MCP Business Tools Server

A production-ready Model Context Protocol (MCP) server that provides 10 essential business tools for AI assistants and automation workflows.

## ✨ Features

This MCP server exposes 10 powerful business tools:

1. **🔍 Web Search** - Search the web using SerpAPI or Google Custom Search
2. **💾 Database Query** - Query MongoDB, PostgreSQL, MySQL, or SQLite databases
3. **🏢 CRM Operations** - Interact with HubSpot and Salesforce CRM systems
4. **💎 Data Enrichment** - Enrich contact/company data via Clearbit or People Data Labs
5. **📅 Calendar Management** - Manage Google Calendar and Outlook appointments
6. **📱 Twilio Communication** - Send SMS, WhatsApp messages, or make voice calls
7. **📧 Email Services** - Send emails via Gmail SMTP, SendGrid, or Mailgun
8. **💳 Stripe Payments** - Process payments, subscriptions, and invoices
9. **📝 Docs/Knowledge Base** - Interact with Notion and Google Drive
10. **📣 Social Media** - Post to LinkedIn and Twitter/X

## 🎯 Architecture

```
┌─────────────────────────────────────┐
│     AI Assistant (Claude, GPT, etc)  │
│         Uses MCP Protocol             │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      MCP Server Protocol            │
│   (business_tools_mcp.py)           │
│     Async, Non-blocking I/O         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        10 Business Tools            │
├─────────────────────────────────────┤
│ Web | DB | CRM | Calendar | Email   │
│ SMS | Payments | Docs | Social      │
└─────────────────────────────────────┘
```

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- API keys for services you want to use

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Hubspot-CRM-MCP.git
cd Hubspot-CRM-MCP
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Database
DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/dbname

# Web Search
SERPAPI_KEY=your_serpapi_key_here
GOOGLE_CUSTOM_SEARCH_KEY=your_google_key_here
GOOGLE_CUSTOM_SEARCH_CX=your_search_engine_id

# CRM
HUBSPOT_PRIVATE_APP_ACCESS_TOKEN=your_hubspot_token
SALESFORCE_TOKEN=your_salesforce_token

# Data Enrichment
PEOPLE_DATA_LABS_KEY=your_pdl_key
CLEARBIT_API_KEY=your_clearbit_key

# Calendar
GOOGLE_CALENDAR_CREDENTIALS=credentials.json
GOOGLE_CALENDAR_TOKEN=google_calendar_token.pickle

# Communication (Twilio)
TWILIO_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# Email Services
GMAIL_EMAIL_ADDRESS=your.email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
SENDGRID_API_KEY=your_sendgrid_key
MAILGUN_API_KEY=your_mailgun_key

# Payments
STRIPE_API_KEY=your_stripe_key

# Docs/Knowledge Base
NOTION_API_KEY=your_notion_key
GOOGLE_DRIVE_KEY=your_drive_key

# Social Media
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
```

## 🔧 Service-Specific Setup

### Gmail SMTP
1. Enable 2-Factor Authentication in your Google Account
2. Generate an App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Create a new app password for "Mail"
   - Use this password in `GMAIL_APP_PASSWORD`

### Google Calendar
1. Create a project in Google Cloud Console
2. Enable Calendar API
3. Download credentials as `credentials.json`
4. Run the authentication flow (first time only)

### HubSpot CRM
1. Create a Private App in HubSpot
2. Grant necessary scopes (contacts, deals)
3. Copy the access token to `.env`

### Twilio
1. Sign up at https://www.twilio.com
2. Get your Account SID and Auth Token
3. Purchase a phone number for SMS/calls

### Notion
1. Create an integration at https://www.notion.so/my-integrations
2. Copy the Internal Integration Token
3. Share pages/databases with your integration

## 🚀 Running the Server

### Development Mode

```bash
python3 business_tools_mcp.py
```

### Production Mode with PM2

```bash
# Install PM2
npm install -g pm2

# Start the server
pm2 start business_tools_mcp.py --interpreter python3 --name mcp-server

# View logs
pm2 logs mcp-server

# Monitor
pm2 monit
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "business_tools_mcp.py"]
```

Build and run:

```bash
# Build image
docker build -t mcp-business-tools .

# Run container
docker run -d \
  --name mcp-server \
  --env-file .env \
  -p 8080:8080 \
  mcp-business-tools
```

## 📡 MCP Client Configuration

### For Claude Desktop

Add to your Claude configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "business-tools": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/business_tools_mcp.py"],
      "env": {
        "PYTHONPATH": "/path/to/project"
      }
    }
  }
}
```

### For Custom Clients

```python
import mcp

# Connect to the MCP server
async with mcp.ClientSession(
    mcp.StdioServerParameters(
        command="/path/to/venv/bin/python",
        args=["/path/to/business_tools_mcp.py"]
    )
) as session:
    # List available tools
    tools = await session.list_tools()
    
    # Call a tool
    result = await session.call_tool(
        "web_search",
        {"query": "MCP protocol", "num_results": 5}
    )
```

## 📊 Testing

### Quick Test

Test if the server is working:

```bash
# Check server startup
python3 -c "import business_tools_mcp; print('✅ Server module loads correctly')"

# Test specific tool
python3 -c "
import asyncio
from business_tools_mcp import web_search_tool

async def test():
    result = await web_search_tool({'query': 'test'})
    print('✅ Tool execution works')

asyncio.run(test())
"
```

### Integration Testing

Create a test script to verify all tools:

```python
import asyncio
from business_tools_mcp import *

async def test_all_tools():
    # Test each tool with minimal parameters
    tools = [
        (web_search_tool, {"query": "test"}),
        (database_query_tool, {"query": "SELECT 1"}),
        # Add more tests as needed
    ]
    
    for tool, params in tools:
        try:
            result = await tool(params)
            print(f"✅ {tool.__name__} works")
        except Exception as e:
            print(f"❌ {tool.__name__} failed: {e}")

asyncio.run(test_all_tools())
```

## 🔐 Security Best Practices

1. **Never commit `.env` files** - Use `.gitignore`
2. **Use environment variables** - Don't hardcode secrets
3. **Rotate API keys regularly** - Especially in production
4. **Use read-only database users** - When possible
5. **Implement rate limiting** - Prevent API abuse
6. **Use HTTPS in production** - Encrypt all communications
7. **Audit logs** - Track all tool usage

## 📈 Monitoring

### Health Check Endpoint

The server provides health status through logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Metrics to Monitor

- Tool execution count
- Response times
- Error rates
- API rate limits
- Database connection pool

## 🐛 Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

**Tool returns "not configured":**
- Check if API key is set in `.env`
- Verify API key is valid
- Check service-specific setup steps

**Database connection fails:**
```bash
# Test MongoDB connection
python3 -c "from pymongo import MongoClient; client = MongoClient('your_url'); client.admin.command('ping')"

# Test SQL connection
python3 -c "import sqlalchemy; engine = sqlalchemy.create_engine('your_url'); engine.connect()"
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 🙋 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Consult the MCP documentation

## 🎯 Roadmap

- [ ] Add more CRM systems (Pipedrive, Zoho)
- [ ] Implement caching layer
- [ ] Add webhook support
- [ ] Create web UI for configuration
- [ ] Add more payment providers
- [ ] Implement batch operations
- [ ] Add GraphQL endpoint

## 🏆 Production Checklist

Before deploying to production:

- [ ] All API keys configured
- [ ] Error handling tested
- [ ] Logging configured
- [ ] Rate limiting implemented
- [ ] Backup strategy defined
- [ ] Monitoring setup
- [ ] Security audit completed
- [ ] Documentation updated
- [ ] Load testing performed
- [ ] Rollback plan prepared

---

**Built with ❤️ using the Model Context Protocol**
