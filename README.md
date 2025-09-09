# Business Tools MCP Server with Gemini AI 🚀

A comprehensive MCP (Model Context Protocol) server providing 10 essential business tools, powered by Google's Gemini AI for intelligent orchestration. This LLM-agnostic system works with any AI model while featuring deep Gemini integration.

## 🌟 Features

### 🛠️ 10 Business Tools Available:
1. **Web Search** - Search the web using SerpAPI/Google Custom Search
2. **Database Query** - Query PostgreSQL/MySQL/SQLite databases
3. **CRM Operations** - HubSpot & Salesforce integration
4. **Data Enrichment** - Clearbit & People Data Labs APIs
5. **Calendar Management** - Google Calendar & Outlook integration
6. **Twilio Communication** - SMS, Voice, WhatsApp messaging
7. **Email Services** - SendGrid & Mailgun transactional emails
8. **Stripe Payments** - Payment processing & subscriptions
9. **Docs/Knowledge Base** - Notion & Google Drive integration
10. **Social Media** - LinkedIn & Twitter/X posting

### 🤖 Gemini AI Integration:
- **Intelligent Tool Selection** - Gemini analyzes requests and selects appropriate tools
- **Action Planning** - Creates step-by-step execution plans
- **Priority Assessment** - Determines task urgency
- **Natural Language Processing** - Understands complex business requests

### 📂 Clean Project Structure:
```
Hubspot-CRM-MCP/
├── business_tools_mcp.py        # Main MCP server with 10 tools
├── demo_gemini_business_tools.py # Gemini AI demo
├── hubspot_mcp.py               # Original HubSpot MCP server
├── config.py                    # Centralized configuration
├── llm_client.py                # LLM provider abstraction
├── .env                         # Your API keys (Gemini configured!)
├── .env.example                 # Template for environment variables
├── requirements.txt             # Python dependencies
├── mcp_config.json             # MCP client configuration
├── run_server.sh               # Server launcher script
├── WARP.md                     # Development documentation
└── README.md                   # This file
```

## 🎯 MCP Tools Available

### Core MCP Tools:
- **`create_contact`** - Creates new contacts with email, name, phone, company
- **`create_deal`** - Creates deals with name, amount, pipeline, stage
- **`associate_contact_deal`** - Links contacts to deals
- **`get_deal`** - Retrieves deals with optional associations
- **`get_contact`** - Retrieves contact information
- **`search_contacts`** - Search contacts by email

### MCP Server Features:
- **Proper MCP Protocol** - Full compliance with MCP specification
- **JSON Schema Validation** - Type-safe tool parameters
- **Error Handling** - Structured error responses
- **Async Support** - Non-blocking operations
- **Legacy API Compatibility** - Uses reliable v3 associations API

## 🚀 Usage

### Run the MCP Server:
```bash
./run_server.sh
# OR manually:
source hubspot-env/bin/activate
python hubspot_mcp.py
```

### Test MCP Server:
```bash
source hubspot-env/bin/activate
python test_simple.py
```

### Test API Connection:
```bash
source hubspot-env/bin/activate
python test_connection.py
```

### MCP Client Integration:
Use the `mcp_config.json` file to configure MCP clients to connect to this server.

## 📊 Recent Test Results

**MCP Server Test Results:**
```
🧪 Testing HubSpot MCP Server
1️⃣ Creating contact...
✅ Contact created: 238651848393
2️⃣ Creating deal...
✅ Deal created: 157307868899
3️⃣ Creating association...
✅ Association created
4️⃣ Retrieving deal...
✅ Deal retrieved: MCP Test Deal 1757326784
   Associated contacts: 1

🎉 All tests passed!
📊 Summary: Contact 238651848393 ↔ Deal 157307868899
```

## 🔑 Required HubSpot Scopes

Your HubSpot Private App needs these permissions:
- `crm.objects.contacts` (read & write)
- `crm.objects.deals` (read & write)
- `crm.schemas.deals` (read & write)

## 🛠 Fixes Applied

1. **Import Issues**: Fixed `ApiException` imports from correct modules
2. **Association API**: Switched to legacy v3 batch API for reliability
3. **SSL Certificates**: Installed macOS certificates for HTTPS requests
4. **Unique Data**: Auto-generated timestamps prevent duplicate conflicts
5. **Error Handling**: Improved exception handling across all functions

## 🎉 Status: MCP Server Production Ready!

The HubSpot MCP Server is fully functional and ready for:
- **MCP Client Integration** - Works with any MCP-compatible client
- **Tool-based CRM Operations** - All core CRM functions available as tools
- **Structured Data Responses** - JSON-formatted responses with success/error handling
- **Async Operations** - Non-blocking server architecture
- **Production Deployment** - Ready for containerization and scaling

### Available MCP Tools:
1. `create_contact` - Create new contacts
2. `create_deal` - Create new deals
3. `associate_contact_deal` - Link contacts and deals
4. `get_deal` - Retrieve deal information
5. `get_contact` - Retrieve contact information
6. `search_contacts` - Search for contacts

---
**Last Updated**: September 8, 2025  
**Status**: ✅ MCP Server operational and tested
