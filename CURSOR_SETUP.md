# HubSpot MCP Server - Cursor IDE Setup

## 🎯 Quick Setup for Cursor IDE

### 1. **Add MCP Server to Cursor**

In Cursor IDE, go to **Settings → Extensions → MCP Servers** and add this configuration:

```json
{
  "mcpServers": {
    "hubspot-crm": {
      "command": "/Users/arsalankhan/Documents/GitHub/Hubspot-CRM-MCP/hubspot-env/bin/python",
      "args": ["/Users/arsalankhan/Documents/GitHub/Hubspot-CRM-MCP/hubspot_mcp.py"]
    }
  }
}
```

### 2. **Restart Cursor IDE**

After adding the configuration, restart Cursor IDE to load the MCP server.

### 3. **Verify Tools Are Available**

You should now see these HubSpot tools available in Cursor:

- 🧑‍💼 **`create_contact`** - Create new contacts
- 💼 **`create_deal`** - Create new deals  
- 🔗 **`associate_contact_deal`** - Link contacts to deals
- 📄 **`get_deal`** - Get deal information

## 🧪 Test the Integration

Try asking Cursor to:

> "Create a new contact named John Doe with email john.doe@example.com"

> "Create a deal called 'Q4 Sales Opportunity' for $25000"

> "Associate contact ID 123456 with deal ID 789012"

## 🛠 Troubleshooting

### No Tools Showing?

1. **Check the path**: Make sure the paths in the config are correct
2. **Test the server manually**:
   ```bash
   cd /Users/arsalankhan/Documents/GitHub/Hubspot-CRM-MCP
   ./run_server.sh
   ```
3. **Check environment**: Ensure `.env` file contains your HubSpot token
4. **Restart Cursor**: Sometimes a full restart is needed

### Server Not Starting?

1. **Test virtual environment**:
   ```bash
   source hubspot-env/bin/activate
   python hubspot_mcp.py
   ```
2. **Check dependencies**:
   ```bash
   source hubspot-env/bin/activate
   pip list | grep -E "(hubspot|mcp|python-dotenv)"
   ```

### Tools Working But Getting Errors?

1. **Check HubSpot token**: Verify your API token in `.env` file
2. **Check permissions**: Ensure your HubSpot Private App has required scopes:
   - `crm.objects.contacts` (read & write)
   - `crm.objects.deals` (read & write)
   - `crm.schemas.deals` (read & write)

## 📊 Expected Results

When working correctly, you should see:

- ✅ **Tools appear** in Cursor's available functions
- ✅ **Commands execute** and return structured JSON responses
- ✅ **Data syncs** with your HubSpot CRM in real-time
- ✅ **Error handling** provides clear feedback on issues

## 🎉 Success!

Your HubSpot MCP server is now integrated with Cursor IDE and ready for use!

---

**Server Status**: ✅ Operational  
**Last Tested**: September 8, 2025  
**Cursor Compatibility**: ✅ Verified
