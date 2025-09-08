#!/usr/bin/env python3

import asyncio
import json
import os
from typing import Any, Dict

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server

from dotenv import load_dotenv
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate
from hubspot.crm.deals import SimplePublicObjectInputForCreate as DealInputForCreate
from hubspot.crm.associations import BatchInputPublicAssociation, PublicAssociation

# Load environment variables
load_dotenv()

# Initialize HubSpot client
access_token = os.getenv("HUBSPOT_PRIVATE_APP_ACCESS_TOKEN")
if not access_token:
    raise ValueError("HUBSPOT_PRIVATE_APP_ACCESS_TOKEN not found")

hubspot_client = HubSpot(access_token=access_token)

# Create server
app = Server("hubspot-crm")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="create_contact",
            description="Create a new contact in HubSpot CRM",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "Contact email"},
                    "firstname": {"type": "string", "description": "First name"},
                    "lastname": {"type": "string", "description": "Last name"},
                    "phone": {"type": "string", "description": "Phone number (optional)"},
                },
                "required": ["email", "firstname", "lastname"]
            }
        ),
        types.Tool(
            name="create_deal",
            description="Create a new deal in HubSpot CRM",
            inputSchema={
                "type": "object",
                "properties": {
                    "dealname": {"type": "string", "description": "Deal name"},
                    "amount": {"type": "string", "description": "Deal amount"},
                    "pipeline": {"type": "string", "description": "Pipeline ID", "default": "default"},
                    "dealstage": {"type": "string", "description": "Deal stage", "default": "appointmentscheduled"}
                },
                "required": ["dealname", "amount"]
            }
        ),
        types.Tool(
            name="associate_contact_deal", 
            description="Associate a contact with a deal",
            inputSchema={
                "type": "object",
                "properties": {
                    "contact_id": {"type": "string", "description": "Contact ID"},
                    "deal_id": {"type": "string", "description": "Deal ID"}
                },
                "required": ["contact_id", "deal_id"]
            }
        ),
        types.Tool(
            name="get_deal",
            description="Get deal information",
            inputSchema={
                "type": "object", 
                "properties": {
                    "deal_id": {"type": "string", "description": "Deal ID"}
                },
                "required": ["deal_id"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(
    name: str, 
    arguments: dict[str, Any] | None
) -> list[types.TextContent]:
    """Handle tool calls"""
    
    if not arguments:
        arguments = {}
    
    try:
        if name == "create_contact":
            return await create_contact(arguments)
        elif name == "create_deal":
            return await create_deal(arguments) 
        elif name == "associate_contact_deal":
            return await associate_contact_deal(arguments)
        elif name == "get_deal":
            return await get_deal(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

async def create_contact(args: Dict[str, Any]) -> list[types.TextContent]:
    """Create a new contact"""
    properties = {
        "email": args["email"],
        "firstname": args["firstname"],
        "lastname": args["lastname"]
    }
    
    if "phone" in args:
        properties["phone"] = args["phone"]
    
    contact_input = SimplePublicObjectInputForCreate(properties=properties)
    api_response = hubspot_client.crm.contacts.basic_api.create(
        simple_public_object_input_for_create=contact_input
    )
    
    result = {
        "success": True,
        "contact_id": api_response.id,
        "email": api_response.properties.get("email"),
        "name": f"{api_response.properties.get('firstname')} {api_response.properties.get('lastname')}"
    }
    
    return [types.TextContent(
        type="text", 
        text=json.dumps(result, indent=2)
    )]

async def create_deal(args: Dict[str, Any]) -> list[types.TextContent]:
    """Create a new deal"""
    properties = {
        "dealname": args["dealname"],
        "amount": args["amount"],
        "pipeline": args.get("pipeline", "default"),
        "dealstage": args.get("dealstage", "appointmentscheduled")
    }
    
    deal_input = DealInputForCreate(properties=properties)
    api_response = hubspot_client.crm.deals.basic_api.create(
        simple_public_object_input_for_create=deal_input
    )
    
    result = {
        "success": True,
        "deal_id": api_response.id,
        "dealname": api_response.properties.get("dealname"),
        "amount": api_response.properties.get("amount")
    }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]

async def associate_contact_deal(args: Dict[str, Any]) -> list[types.TextContent]:
    """Associate a contact with a deal"""
    contact_id = args["contact_id"]
    deal_id = args["deal_id"]
    
    association_input = BatchInputPublicAssociation(
        inputs=[
            PublicAssociation(
                _from={"id": contact_id},
                to={"id": deal_id},
                type="contact_to_deal"
            )
        ]
    )
    
    hubspot_client.crm.associations.batch_api.create(
        from_object_type="contact",
        to_object_type="deal",
        batch_input_public_association=association_input
    )
    
    result = {
        "success": True,
        "message": f"Associated contact {contact_id} with deal {deal_id}"
    }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]

async def get_deal(args: Dict[str, Any]) -> list[types.TextContent]:
    """Get deal information"""
    deal_id = args["deal_id"]
    
    deal = hubspot_client.crm.deals.basic_api.get_by_id(
        deal_id,
        properties=["dealname", "amount", "dealstage"],
        associations=["contacts"]
    )
    
    result = {
        "success": True,
        "deal_id": deal.id,
        "dealname": deal.properties.get("dealname"),
        "amount": deal.properties.get("amount"),
        "stage": deal.properties.get("dealstage")
    }
    
    if deal.associations and deal.associations.get("contacts"):
        result["associated_contacts"] = len(deal.associations["contacts"].results)
    
    return [types.TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
