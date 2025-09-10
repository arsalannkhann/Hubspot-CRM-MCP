# MCP Business Tools Server - Deployment Guide

## Overview
A production-ready Model Context Protocol (MCP) server providing structured JSON APIs for business tools integration including HubSpot CRM, Google Calendar, Notion, Google Drive, and Twitter/X social media posting.

## Prerequisites

### System Requirements
- Python 3.8 or higher
- pip (Python package manager)
- Unix-like environment (macOS, Linux) or Windows with WSL

### Required API Credentials
You'll need API credentials for the services you plan to use:
- **HubSpot**: Private App Access Token
- **Google Calendar**: OAuth2 credentials (credentials.json)
- **Notion**: Integration token and database ID
- **Google Drive**: Service account credentials or OAuth2
- **Twitter/X**: OAuth Bearer Token

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/Hubspot-CRM-MCP.git
cd Hubspot-CRM-MCP
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy the example environment file and configure with your credentials:
```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:
```env
# HubSpot Configuration
HUBSPOT_ACCESS_TOKEN=your_hubspot_private_app_token

# Google Calendar Configuration
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials.json

# Notion Configuration
NOTION_API_KEY=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id

# Twitter/X Configuration
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# Google Drive Configuration (optional)
GOOGLE_DRIVE_CREDENTIALS_PATH=drive_credentials.json
```

## Running the Server

### Standard Mode
```bash
python3 business_tools_mcp.py
```

The server will start on the default MCP stdio interface.

### With Claude Desktop
1. Edit Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):
```json
{
  "mcpServers": {
    "business-tools": {
      "command": "python3",
      "args": ["/path/to/Hubspot-CRM-MCP/business_tools_mcp.py"],
      "env": {
        "PYTHONPATH": "/path/to/Hubspot-CRM-MCP"
      }
    }
  }
}
```

2. Restart Claude Desktop

### As a Service (systemd on Linux)
Create `/etc/systemd/system/mcp-business-tools.service`:
```ini
[Unit]
Description=MCP Business Tools Server
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/Hubspot-CRM-MCP
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /path/to/Hubspot-CRM-MCP/business_tools_mcp.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mcp-business-tools
sudo systemctl start mcp-business-tools
```

## Available Tools

### 1. HubSpot CRM Operations
- `hubspot_create_contact`: Create new contacts
- `hubspot_update_contact`: Update existing contacts
- `hubspot_search_contacts`: Search contacts with filters
- `hubspot_create_company`: Create companies
- `hubspot_create_deal`: Create deals
- `hubspot_create_task`: Create tasks

### 2. Google Calendar
- `google_calendar_create_event`: Create calendar events
- `google_calendar_list_events`: List upcoming events
- `google_calendar_update_event`: Update existing events

### 3. Notion Database
- `notion_create_page`: Create pages in database
- `notion_search_pages`: Search database pages
- `notion_update_page`: Update existing pages

### 4. Social Media (Twitter/X)
- `social_media_post`: Post to Twitter with dry-run support

### 5. Google Drive
- `google_drive_upload`: Upload files
- `google_drive_search`: Search files
- `google_drive_share`: Share files

## Testing the Deployment

### 1. Test Connection
```bash
# Test server startup
python3 business_tools_mcp.py &
PID=$!
sleep 2
kill $PID

# Check for errors
echo "Server started successfully if no errors above"
```

### 2. Test Individual Tools
Use the MCP client or send test requests:

```python
# test_tools.py
import asyncio
from business_tools_mcp import main

async def test():
    # Test will be handled through MCP protocol
    print("Server is ready for MCP requests")

asyncio.run(test())
```

### 3. Verify Configuration
```bash
# Check environment variables
python3 -c "from config import Config; c = Config(); print('Config loaded successfully')"
```

## Production Considerations

### Security
1. **Never commit `.env` file** - It's in `.gitignore`
2. **Use secure token storage** - Consider using secret management services
3. **Implement rate limiting** - Respect API limits
4. **Use HTTPS** - If exposing endpoints
5. **Rotate credentials regularly**

### Monitoring
1. **Logging**: Server logs to stderr by default
2. **Health checks**: Implement endpoint monitoring
3. **Error tracking**: Consider Sentry or similar
4. **Metrics**: Track API usage and response times

### Scaling
1. **Async operations**: Server uses asyncio for concurrent requests
2. **Connection pooling**: Reuse API connections
3. **Caching**: Implement response caching where appropriate
4. **Load balancing**: Use reverse proxy for multiple instances

## Troubleshooting

### Common Issues

#### 1. Module Not Found
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt
```

#### 2. Permission Denied
```bash
# Make script executable
chmod +x business_tools_mcp.py
```

#### 3. API Authentication Errors
- Verify credentials in `.env`
- Check API token expiration
- Ensure proper scopes/permissions

#### 4. Google Calendar Token Issues
```bash
# Remove old token and re-authenticate
rm google_calendar_token.pickle
python3 business_tools_mcp.py
```

### Debug Mode
Set logging level in the code:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Maintenance

### Updates
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Backup
Regular backup of:
- `.env` file (securely)
- `google_calendar_token.pickle`
- Any local credentials

### Log Rotation
Configure logrotate for production:
```bash
/var/log/mcp-business-tools/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

## Support

For issues or questions:
1. Check error logs
2. Verify API credentials
3. Test individual tools
4. Review this documentation

## License

[Your License Here]

---

Last updated: September 2024
