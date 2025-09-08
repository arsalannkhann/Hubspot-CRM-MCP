#!/usr/bin/env python3
"""
Test script for HubSpot MCP Server

This script tests the MCP server by calling its tools directly.
"""

import json
import time
from mcp.types import CallToolRequest

# Simulate MCP tool calls for testing
async def test_mcp_tools():
    """Test all MCP tools"""
    from hubspot_mcp_server import HubSpotMCPServer
    
    print("🧪 Testing HubSpot MCP Server Tools")
    print("=" * 50)
    
    # Initialize server
    server = HubSpotMCPServer()
    
    # Generate unique timestamp for test data
    timestamp = int(time.time())
    unique_email = f"mcp-test-{timestamp}@example.com"
    
    # Test 1: List tools
    print("1️⃣ Testing list_tools...")
    tools_response = await server._register_handlers.__wrapped__(server)
    list_tools = None
    for handler in server.server._tool_handlers:
        if hasattr(handler, '__name__') and 'list_tools' in handler.__name__:
            list_tools = await handler()
            break
    
    if list_tools:
        print(f"✅ Found {len(list_tools.tools)} tools:")
        for tool in list_tools.tools:
            print(f"   • {tool.name}: {tool.description}")
    else:
        print("❌ Could not list tools")
    
    print()
    
    # Test 2: Create contact
    print("2️⃣ Testing create_contact...")
    contact_request = CallToolRequest(
        name="create_contact",
        arguments={
            "email": unique_email,
            "firstname": "MCP Test",
            "lastname": "Contact",
            "phone": "555-123-4567",
            "company": "Test Company"
        }
    )
    
    contact_result = await server._create_contact(contact_request.arguments)
    contact_data = json.loads(contact_result.content[0].text)
    
    if contact_data.get("success"):
        print(f"✅ Contact created: {contact_data['contact_id']}")
        contact_id = contact_data['contact_id']
    else:
        print(f"❌ Contact creation failed: {contact_data.get('error')}")
        return
    
    print()
    
    # Test 3: Create deal
    print("3️⃣ Testing create_deal...")
    deal_request = CallToolRequest(
        name="create_deal",
        arguments={
            "dealname": f"MCP Test Deal - {timestamp}",
            "amount": "5000.00",
            "pipeline": "default",
            "dealstage": "appointmentscheduled"
        }
    )
    
    deal_result = await server._create_deal(deal_request.arguments)
    deal_data = json.loads(deal_result.content[0].text)
    
    if deal_data.get("success"):
        print(f"✅ Deal created: {deal_data['deal_id']}")
        deal_id = deal_data['deal_id']
    else:
        print(f"❌ Deal creation failed: {deal_data.get('error')}")
        return
    
    print()
    
    # Test 4: Associate contact with deal
    print("4️⃣ Testing associate_contact_deal...")
    associate_request = CallToolRequest(
        name="associate_contact_deal",
        arguments={
            "contact_id": contact_id,
            "deal_id": deal_id
        }
    )
    
    associate_result = await server._associate_contact_deal(associate_request.arguments)
    associate_data = json.loads(associate_result.content[0].text)
    
    if associate_data.get("success"):
        print(f"✅ Association created: Contact {contact_id} ↔ Deal {deal_id}")
    else:
        print(f"❌ Association failed: {associate_data.get('error')}")
    
    print()
    
    # Test 5: Get deal with associations
    print("5️⃣ Testing get_deal...")
    get_deal_request = CallToolRequest(
        name="get_deal",
        arguments={
            "deal_id": deal_id,
            "include_associations": True
        }
    )
    
    get_deal_result = await server._get_deal(get_deal_request.arguments)
    get_deal_data = json.loads(get_deal_result.content[0].text)
    
    if get_deal_data.get("success"):
        print(f"✅ Deal retrieved: {get_deal_data['properties']['dealname']}")
        print(f"   Amount: ${get_deal_data['properties']['amount']}")
        print(f"   Stage: {get_deal_data['properties']['dealstage']}")
        
        associations = get_deal_data.get("associations", {})
        if "contacts" in associations:
            print(f"   Associated contacts: {len(associations['contacts'])}")
        else:
            print("   No associated contacts found")
    else:
        print(f"❌ Get deal failed: {get_deal_data.get('error')}")
    
    print()
    
    # Test 6: Get contact
    print("6️⃣ Testing get_contact...")
    get_contact_request = CallToolRequest(
        name="get_contact",
        arguments={
            "contact_id": contact_id
        }
    )
    
    get_contact_result = await server._get_contact(get_contact_request.arguments)
    get_contact_data = json.loads(get_contact_result.content[0].text)
    
    if get_contact_data.get("success"):
        props = get_contact_data['properties']
        print(f"✅ Contact retrieved: {props.get('firstname')} {props.get('lastname')}")
        print(f"   Email: {props.get('email')}")
        print(f"   Phone: {props.get('phone')}")
        print(f"   Company: {props.get('company')}")
    else:
        print(f"❌ Get contact failed: {get_contact_data.get('error')}")
    
    print()
    
    # Test 7: Search contacts
    print("7️⃣ Testing search_contacts...")
    search_request = CallToolRequest(
        name="search_contacts",
        arguments={
            "email": unique_email,
            "limit": 5
        }
    )
    
    search_result = await server._search_contacts(search_request.arguments)
    search_data = json.loads(search_result.content[0].text)
    
    if search_data.get("success"):
        print(f"✅ Search completed: Found {search_data['total']} contacts")
        for contact in search_data.get('contacts', []):
            props = contact['properties']
            print(f"   • {props.get('firstname')} {props.get('lastname')} ({props.get('email')})")
    else:
        print(f"❌ Search failed: {search_data.get('error')}")
    
    print()
    print("🎉 MCP Server testing completed!")
    print(f"📊 Test Summary:")
    print(f"   Contact ID: {contact_id}")
    print(f"   Deal ID: {deal_id}")
    print(f"   Email: {unique_email}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_mcp_tools())
