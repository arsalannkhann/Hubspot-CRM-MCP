#!/usr/bin/env python3
"""
Simple test for HubSpot MCP Server tools
"""

import asyncio
import json
import time

async def test_hubspot_mcp():
    from hubspot_mcp_server import HubSpotMCPServer
    
    print("🧪 Testing HubSpot MCP Server")
    print("=" * 40)
    
    # Initialize server
    server = HubSpotMCPServer()
    timestamp = int(time.time())
    
    # Test create contact
    print("1️⃣ Creating contact...")
    contact_args = {
        "email": f"mcp-test-{timestamp}@example.com",
        "firstname": "MCP",
        "lastname": "Test",
        "phone": "555-123-4567"
    }
    
    contact_result = await server._create_contact(contact_args)
    contact_data = json.loads(contact_result.content[0].text)
    
    if contact_data.get("success"):
        print(f"✅ Contact created: {contact_data['contact_id']}")
        contact_id = contact_data['contact_id']
        
        # Test create deal
        print("2️⃣ Creating deal...")
        deal_args = {
            "dealname": f"MCP Test Deal {timestamp}",
            "amount": "7500.00"
        }
        
        deal_result = await server._create_deal(deal_args)
        deal_data = json.loads(deal_result.content[0].text)
        
        if deal_data.get("success"):
            print(f"✅ Deal created: {deal_data['deal_id']}")
            deal_id = deal_data['deal_id']
            
            # Test association
            print("3️⃣ Creating association...")
            assoc_args = {
                "contact_id": contact_id,
                "deal_id": deal_id
            }
            
            assoc_result = await server._associate_contact_deal(assoc_args)
            assoc_data = json.loads(assoc_result.content[0].text)
            
            if assoc_data.get("success"):
                print(f"✅ Association created")
                
                # Test get deal
                print("4️⃣ Retrieving deal...")
                get_args = {"deal_id": deal_id}
                get_result = await server._get_deal(get_args)
                get_data = json.loads(get_result.content[0].text)
                
                if get_data.get("success"):
                    print(f"✅ Deal retrieved: {get_data['properties']['dealname']}")
                    
                    associations = get_data.get("associations", {})
                    contact_count = len(associations.get("contacts", []))
                    print(f"   Associated contacts: {contact_count}")
                    
                    print("\n🎉 All tests passed!")
                    print(f"📊 Summary: Contact {contact_id} ↔ Deal {deal_id}")
                else:
                    print(f"❌ Failed to retrieve deal: {get_data.get('error')}")
            else:
                print(f"❌ Failed to create association: {assoc_data.get('error')}")
        else:
            print(f"❌ Failed to create deal: {deal_data.get('error')}")
    else:
        print(f"❌ Failed to create contact: {contact_data.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_hubspot_mcp())
