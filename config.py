"""
Configuration file for Business Tools MCP Server
Centralized API keys and LLM provider settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================
# LLM PROVIDER CONFIGURATION
# ============================================

# Choose your LLM provider: "gemini", "llama3", "openai", "claude", "custom"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

# LLM API Keys (only needed if using cloud-based LLMs)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Local LLM Settings (for Llama3 or other local models)
LOCAL_LLM_HOST = os.getenv("LOCAL_LLM_HOST", "http://localhost:11434")  # Ollama default
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "llama3")

# ============================================
# BUSINESS TOOL API KEYS
# ============================================

# 1. Web Search
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
GOOGLE_CUSTOM_SEARCH_KEY = os.getenv("GOOGLE_CUSTOM_SEARCH_KEY", "")
GOOGLE_CUSTOM_SEARCH_CX = os.getenv("GOOGLE_CUSTOM_SEARCH_CX", "")

# 2. Database
DATABASE_URL = os.getenv("DATABASE_URL", "")
# Examples:
# PostgreSQL: postgresql://user:password@localhost/dbname
# MySQL: mysql://user:password@localhost/dbname
# SQLite: sqlite:///path/to/database.db

# 3. CRM Integration
HUBSPOT_TOKEN = os.getenv("HUBSPOT_PRIVATE_APP_ACCESS_TOKEN", "")
SALESFORCE_TOKEN = os.getenv("SALESFORCE_TOKEN", "")
SALESFORCE_DOMAIN = os.getenv("SALESFORCE_DOMAIN", "")

# 4. Data Enrichment
CLEARBIT_KEY = os.getenv("CLEARBIT_KEY", "")
PEOPLE_DATA_LABS_KEY = os.getenv("PEOPLE_DATA_LABS_KEY", "")

# 5. Calendar & Appointments
GOOGLE_CALENDAR_CREDENTIALS = os.getenv("GOOGLE_CALENDAR_CREDENTIALS", "")
OUTLOOK_CLIENT_ID = os.getenv("OUTLOOK_CLIENT_ID", "")
OUTLOOK_CLIENT_SECRET = os.getenv("OUTLOOK_CLIENT_SECRET", "")

# 6. Twilio Communication
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_API_KEY_SID = os.getenv("TWILIO_API_KEY_SID", "")
TWILIO_API_KEY_SECRET = os.getenv("TWILIO_API_KEY_SECRET", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "")

# 7. Email Services
SENDGRID_KEY = os.getenv("SENDGRID_KEY", "")
MAILGUN_KEY = os.getenv("MAILGUN_KEY", "")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN", "")
EMAIL_FROM_ADDRESS = os.getenv("EMAIL_FROM_ADDRESS", "noreply@example.com")

# 8. Stripe Payments
STRIPE_KEY = os.getenv("STRIPE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# 9. Docs/Knowledge Base
NOTION_KEY = os.getenv("NOTION_KEY", "")
GOOGLE_DRIVE_KEY = os.getenv("GOOGLE_DRIVE_KEY", "")
GOOGLE_DRIVE_CREDENTIALS = os.getenv("GOOGLE_DRIVE_CREDENTIALS", "")

# 10. Social Media
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")

# ============================================
# SERVER CONFIGURATION
# ============================================

# MCP Server Settings
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "business-tools")
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "5000"))
MCP_LOG_LEVEL = os.getenv("MCP_LOG_LEVEL", "INFO")

# Security Settings
ENABLE_AUTH = os.getenv("ENABLE_AUTH", "false").lower() == "true"
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")

# Rate Limiting
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # seconds

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_configured_tools():
    """
    Returns a list of tools that have been configured with API keys
    """
    configured = []
    
    if SERPAPI_KEY or GOOGLE_CUSTOM_SEARCH_KEY:
        configured.append("web_search")
    if DATABASE_URL:
        configured.append("database_query")
    if HUBSPOT_TOKEN or SALESFORCE_TOKEN:
        configured.append("crm_operation")
    if CLEARBIT_KEY or PEOPLE_DATA_LABS_KEY:
        configured.append("enrich_data")
    if GOOGLE_CALENDAR_CREDENTIALS or OUTLOOK_CLIENT_ID:
        configured.append("calendar_operation")
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        configured.append("twilio_communication")
    if SENDGRID_KEY or MAILGUN_KEY:
        configured.append("send_email")
    if STRIPE_KEY:
        configured.append("stripe_operation")
    if NOTION_KEY or GOOGLE_DRIVE_KEY:
        configured.append("docs_operation")
    if LINKEDIN_ACCESS_TOKEN or TWITTER_BEARER_TOKEN:
        configured.append("social_media_post")
    
    return configured

def validate_configuration():
    """
    Validates that at least some tools are configured
    """
    configured = get_configured_tools()
    
    if not configured:
        print("⚠️  Warning: No tools are configured with API keys.")
        print("   Please add API keys to your .env file to enable tools.")
        print("   See .env.example for required keys.")
    else:
        print(f"✅ {len(configured)} tools configured and ready:")
        for tool in configured:
            print(f"   - {tool}")
    
    return len(configured) > 0

# Run validation on import
if __name__ == "__main__":
    validate_configuration()
