#!/usr/bin/env python3

import os
import ssl
from dotenv import load_dotenv
from hubspot import HubSpot
from hubspot.crm.contacts import ApiException

# Load environment variables
load_dotenv()
access_token = os.getenv("HUBSPOT_PRIVATE_APP_ACCESS_TOKEN")

if not access_token:
    print("❌ Error: HubSpot access token not found in .env file")
    exit(1)

print("🔑 Access token found")
print(f"Token preview: {access_token[:15]}...")

# Initialize HubSpot client
try:
    client = HubSpot(access_token=access_token)
    print("✅ HubSpot client initialized successfully")
    
    # Test API connection by getting account info
    print("🔄 Testing API connection...")
    
    # Try to get contact properties to test connection
    properties = client.crm.properties.core_api.get_all(object_type="contacts")
    print(f"✅ API connection successful! Found {len(properties.results)} contact properties")
    
    # Show some sample properties
    print("\n📋 Sample contact properties:")
    for i, prop in enumerate(properties.results[:5]):
        print(f"  {i+1}. {prop.name} ({prop.label})")
    
except ApiException as e:
    print(f"❌ API Error: {e}")
    if hasattr(e, 'status'):
        if e.status == 401:
            print("   This usually means your access token is invalid")
        elif e.status == 403:
            print("   This usually means your app doesn't have the required permissions")
    
except ssl.SSLError as e:
    print(f"❌ SSL Error: {e}")
    print("   This is a common issue on macOS. Trying to install certificates...")
    print("   Run: /Applications/Python\\ 3.10/Install\\ Certificates.command")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print("\n🏁 Connection test complete")
