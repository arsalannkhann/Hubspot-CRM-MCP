# ⚡ Quick Start Guide

Get your MCP Business Tools Server running in 5 minutes!

## 🎯 Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Git installed
- [ ] At least one API key (e.g., HubSpot, Gmail, or Twilio)

## 🚀 Step 1: Clone & Setup (1 minute)

```bash
# Clone the repository
git clone https://github.com/yourusername/Hubspot-CRM-MCP.git
cd Hubspot-CRM-MCP

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## 📦 Step 2: Install Dependencies (2 minutes)

```bash
pip install -r requirements.txt
```

## 🔑 Step 3: Configure API Keys (2 minutes)

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

**Minimum configuration** - Add at least one:

```env
# Option 1: HubSpot CRM
HUBSPOT_PRIVATE_APP_ACCESS_TOKEN=your_token_here

# Option 2: Gmail
GMAIL_EMAIL_ADDRESS=your.email@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here

# Option 3: Twilio SMS
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

## ▶️ Step 4: Run the Server

```bash
python3 business_tools_mcp.py
```

## ✅ Step 5: Verify It's Working

```bash
# In a new terminal, test the server
python3 -c "
import asyncio
from business_tools_mcp import calendar_operation_tool

async def test():
    result = await calendar_operation_tool({
        'provider': 'google',
        'action': 'get_events',
        'data': {'max_results': 1}
    })
    print('✅ Server is working!')

asyncio.run(test())
"
```

## 🎉 You're Ready!

Your MCP server is now running with these tools available:

| Tool | Status | Example Usage |
|------|--------|---------------|
| 🔍 Web Search | Ready* | Search web for information |
| 💾 Database | Ready* | Query your database |
| 🏢 CRM | Ready* | Manage contacts & deals |
| 💎 Data Enrichment | Ready* | Enrich contact data |
| 📅 Calendar | Ready | Manage appointments |
| 📱 SMS/WhatsApp | Ready* | Send messages |
| 📧 Email | Ready* | Send emails |
| 💳 Payments | Ready* | Process payments |
| 📝 Docs | Ready* | Manage documents |
| 📣 Social Media | Ready* | Post to social platforms |

*Requires API key configuration

## 🔧 Common Quick Fixes

### Can't install dependencies?
```bash
# Upgrade pip first
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

### Server won't start?
```bash
# Check Python version
python3 --version  # Must be 3.8+

# Check if port is in use
lsof -i :8080
```

### API not working?
```bash
# Test your API key
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('HubSpot:', 'Yes' if os.getenv('HUBSPOT_PRIVATE_APP_ACCESS_TOKEN') else 'No')
print('Gmail:', 'Yes' if os.getenv('GMAIL_EMAIL_ADDRESS') else 'No')
print('Twilio:', 'Yes' if os.getenv('TWILIO_SID') else 'No')
"
```

## 📚 Next Steps

1. **Add more API keys** - Enable more tools by adding keys to `.env`
2. **Read the documentation** - Check `README.md` for detailed setup
3. **Deploy to production** - See `DEPLOYMENT.md` for deployment options
4. **Connect AI assistants** - Integrate with Claude, GPT, or other AI

## 🆘 Need Help?

- 📖 Full documentation: `README.md`
- 🚀 Deployment guide: `DEPLOYMENT.md`
- 🐛 Troubleshooting: Check the logs
- 💬 Support: Open an issue on GitHub

---

**Ready in 5 minutes!** 🎉 Your MCP Business Tools Server is now operational.
