#!/usr/bin/env python3
"""
Test script for MongoDB and Twilio connections
Tests both services and provides detailed feedback
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_mongodb():
    """Test MongoDB connection and basic operations"""
    print("\n" + "="*60)
    print("🔍 TESTING MONGODB CONNECTION")
    print("="*60)
    
    try:
        from pymongo import MongoClient
        from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
        
        # Get MongoDB URL from environment
        mongo_url = os.getenv("DATABASE_URL")
        if not mongo_url:
            print("❌ MongoDB URL not found in environment variables")
            return False
            
        print(f"📍 Connecting to MongoDB...")
        print(f"   URL: {mongo_url[:30]}...")  # Show partial URL for security
        
        # Create client with timeout
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        
        # Get database info
        db_list = client.list_database_names()
        print(f"📊 Available databases: {', '.join(db_list[:5])}")
        
        # Test write operation
        test_db = client.test_database
        test_collection = test_db.test_collection
        
        # Insert test document
        test_doc = {
            "test": True,
            "timestamp": datetime.now(),
            "message": "Connection test successful"
        }
        result = test_collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Read back the document
        found_doc = test_collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print("✅ Successfully read test document back")
        
        # Clean up test document
        test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Test document cleaned up")
        
        # Show collections in test database
        collections = test_db.list_collection_names()
        if collections:
            print(f"📁 Collections in test database: {', '.join(collections[:5])}")
        
        client.close()
        print("\n✅ MongoDB test completed successfully!")
        return True
        
    except ImportError:
        print("❌ pymongo not installed. Install with: pip install pymongo")
        return False
    except ConnectionFailure as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False
    except ServerSelectionTimeoutError:
        print("❌ MongoDB connection timeout. Check your connection string and network.")
        return False
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        return False

def test_twilio():
    """Test Twilio connection and capabilities"""
    print("\n" + "="*60)
    print("📱 TESTING TWILIO CONNECTION")
    print("="*60)
    
    try:
        from twilio.rest import Client
        from twilio.base.exceptions import TwilioRestException
        
        # Get Twilio credentials
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Also get API key credentials if available
        api_key_sid = os.getenv("TWILIO_API_KEY_SID")
        api_key_secret = os.getenv("TWILIO_API_KEY_SECRET")
        
        if not account_sid:
            print("❌ TWILIO_ACCOUNT_SID not found in environment variables")
            return False
            
        if not auth_token:
            print("❌ TWILIO_AUTH_TOKEN not found in environment variables")
            return False
            
        print(f"📍 Connecting to Twilio...")
        print(f"   Account SID: {account_sid[:10]}...")
        print(f"   Phone Number: {phone_number}")
        
        # Create Twilio client
        client = Client(account_sid, auth_token)
        
        # Test account access
        account = client.api.accounts(account_sid).fetch()
        print(f"✅ Successfully connected to Twilio!")
        print(f"   Account Name: {account.friendly_name}")
        print(f"   Account Status: {account.status}")
        print(f"   Account Type: {account.type}")
        
        # Check balance if available
        try:
            balance = client.api.v2010.accounts(account_sid).balance.fetch()
            print(f"💰 Account Balance: {balance.balance} {balance.currency}")
        except:
            print("ℹ️  Balance information not available")
        
        # List available phone numbers
        incoming_phone_numbers = client.incoming_phone_numbers.list(limit=5)
        if incoming_phone_numbers:
            print(f"\n📞 Available Phone Numbers:")
            for number in incoming_phone_numbers:
                capabilities = []
                if number.capabilities.get('voice'):
                    capabilities.append("Voice")
                if number.capabilities.get('SMS'):
                    capabilities.append("SMS")
                if number.capabilities.get('MMS'):
                    capabilities.append("MMS")
                print(f"   {number.phone_number} - {', '.join(capabilities)}")
        
        # Check messaging service
        print(f"\n📨 Messaging Capabilities:")
        if phone_number:
            print(f"   ✅ SMS/MMS ready from {phone_number}")
            
            # Get recent message statistics (if any)
            try:
                messages = client.messages.list(limit=5)
                if messages:
                    print(f"   📊 Recent messages found: {len(messages)}")
                else:
                    print("   ℹ️  No recent messages")
            except:
                print("   ℹ️  Unable to fetch message history")
        else:
            print("   ⚠️  No phone number configured for sending")
        
        # Check for WhatsApp capability
        whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        if whatsapp_number:
            print(f"   ✅ WhatsApp ready from {whatsapp_number}")
        else:
            print("   ℹ️  WhatsApp not configured")
        
        # Test API Key authentication if available
        if api_key_sid and api_key_secret:
            print(f"\n🔑 API Key Authentication:")
            try:
                api_client = Client(api_key_sid, api_key_secret, account_sid)
                # Try a simple operation with API key
                api_account = api_client.api.accounts(account_sid).fetch()
                print(f"   ✅ API Key authentication working")
            except Exception as e:
                print(f"   ⚠️  API Key authentication failed: {e}")
        
        print("\n✅ Twilio test completed successfully!")
        return True
        
    except ImportError:
        print("❌ twilio not installed. Install with: pip install twilio")
        return False
    except TwilioRestException as e:
        print(f"❌ Twilio API error: {e}")
        if "authentication" in str(e).lower():
            print("   Please check your Account SID and Auth Token")
        return False
    except Exception as e:
        print(f"❌ Twilio test failed: {e}")
        return False

def test_gmail():
    """Test Gmail SMTP configuration"""
    print("\n" + "="*60)
    print("📧 TESTING GMAIL SMTP CONFIGURATION")
    print("="*60)
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        # Get Gmail credentials
        smtp_host = os.getenv("GMAIL_SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("GMAIL_SMTP_PORT", "587"))
        email_address = os.getenv("GMAIL_EMAIL_ADDRESS")
        app_password = os.getenv("GMAIL_APP_PASSWORD")
        
        if not email_address or not app_password:
            print("❌ Gmail credentials not found in environment variables")
            return False
            
        print(f"📍 Testing Gmail SMTP connection...")
        print(f"   Email: {email_address}")
        print(f"   Host: {smtp_host}:{smtp_port}")
        
        # Test SMTP connection
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(email_address, app_password)
        print("✅ Successfully authenticated with Gmail SMTP!")
        server.quit()
        
        print("✅ Gmail SMTP test completed successfully!")
        print("   You can now send emails using this configuration")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Gmail authentication failed!")
        print("   Please check:")
        print("   1. 2-factor authentication is enabled")
        print("   2. You're using an App Password (not regular password)")
        print("   3. Generate App Password at: https://myaccount.google.com/apppasswords")
        return False
    except Exception as e:
        print(f"❌ Gmail SMTP test failed: {e}")
        return False

def main():
    """Run all connection tests"""
    print("\n" + "="*60)
    print("🚀 BUSINESS TOOLS MCP - CONNECTION TESTER")
    print("="*60)
    print("Testing configured services...")
    
    results = {
        "MongoDB": test_mongodb(),
        "Twilio": test_twilio(),
        "Gmail SMTP": test_gmail()
    }
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service}: {'PASSED' if status else 'FAILED'}")
    
    # Overall result
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All tests passed! Your services are ready to use.")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
