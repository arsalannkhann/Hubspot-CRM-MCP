# HubSpot CRM MCP (Model Context Protocol) 🚀

A complete HubSpot CRM integration using Python that demonstrates creating contacts, deals, and associations through the HubSpot API.

## 🔧 Setup Complete

### ✅ What's Working:
- **Python Virtual Environment**: `hubspot-env/` 
- **Dependencies Installed**: `hubspot-api-client` v12.0.0 & `python-dotenv`
- **API Authentication**: HubSpot Private App token configured
- **SSL Certificates**: Fixed for macOS compatibility

### 📂 Project Structure:
```
Hubspot-CRM-MCP/
├── hubspot-env/           # Virtual environment
├── mcp.py                 # Main MCP script (WORKING!)
├── demo.py                # Interactive demo script  
├── test_connection.py     # API connection tester
├── .env                   # Your HubSpot credentials
├── .gitignore            # Protects sensitive files
└── README.md             # This file
```

## 🎯 Main Features

### Core Functions:
- **`create_contact()`** - Creates new contacts with email, name, phone
- **`create_deal()`** - Creates deals with name, amount, pipeline, stage
- **`associate_records()`** - Links contacts to deals (uses legacy API for reliability)
- **`get_deal_with_associations()`** - Retrieves deals with linked contacts
- **`handle_api_error()`** - Centralized error handling

### API Compatibility:
- Uses **Legacy Associations API** (v3) for reliable contact-deal linking
- Automatic unique ID generation to prevent conflicts
- Proper error handling for rate limits and validation

## 🚀 Usage

### Run the Main Demo:
```bash
source hubspot-env/bin/activate
python mcp.py
```

### Test API Connection:
```bash
source hubspot-env/bin/activate
python test_connection.py
```

## 📊 Recent Test Results

**Last successful run:**
```
🚀 HubSpot CRM MCP - Starting Demo
✅ Contact created: MCP Demo (ID: 238253631211)
✅ Deal created: MCP Demo Deal - 1757285566 (ID: 157169349361) 
🔗 Associated contacts 238253631211 → deals 157169349361
📊 MCP Status: Ready for production use!
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

## 🎉 Status: Production Ready!

The MCP implementation is fully functional and ready for:
- Integration with larger applications
- Batch processing of contacts/deals
- Custom CRM workflows
- Data synchronization tasks

---
**Last Updated**: September 7, 2025  
**Status**: ✅ All systems operational
