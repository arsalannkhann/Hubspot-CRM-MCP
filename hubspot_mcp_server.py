#!/usr/bin/env python3
"""
HubSpot MCP Server

A Model Context Protocol server that provides tools for interacting with HubSpot CRM.
Supports creating contacts, deals, associations, and retrieving CRM data.
"""

import os
import time
import json
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# MCP imports
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    EmbeddedResource
)

# HubSpot imports  
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate, ApiException as ContactsApiException
from hubspot.crm.deals import SimplePublicObjectInputForCreate as DealInputForCreate
from hubspot.crm.associations import BatchInputPublicAssociation, PublicAssociation

# Load environment variables
load_dotenv()

class HubSpotMCPServer:
    """HubSpot MCP Server implementation"""
    
    def __init__(self):
        self.server = Server("hubspot-crm")
        self.hubspot_client: Optional[HubSpot] = None
        self._setup_hubspot_client()
        self._register_handlers()
    
    def _setup_hubspot_client(self):
        """Initialize HubSpot client with credentials"""
        access_token = os.getenv("HUBSPOT_PRIVATE_APP_ACCESS_TOKEN")
        
        if not access_token:
            raise ValueError("HUBSPOT_PRIVATE_APP_ACCESS_TOKEN not found in environment variables")
        
        self.hubspot_client = HubSpot(access_token=access_token)
    
    def _register_handlers(self):
        """Register MCP request handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available HubSpot CRM tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="create_contact",
                        description="Create a new contact in HubSpot CRM",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "email": {
                                    "type": "string",
                                    "description": "Contact's email address (required, must be unique)"
                                },
                                "firstname": {
                                    "type": "string", 
                                    "description": "Contact's first name"
                                },
                                "lastname": {
                                    "type": "string",
                                    "description": "Contact's last name"
                                },
                                "phone": {
                                    "type": "string",
                                    "description": "Contact's phone number (optional)"
                                },
                                "company": {
                                    "type": "string",
                                    "description": "Contact's company (optional)"
                                }
                            },
                            "required": ["email", "firstname", "lastname"]
                        }
                    ),
                    Tool(
                        name="create_deal",
                        description="Create a new deal in HubSpot CRM",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "dealname": {
                                    "type": "string",
                                    "description": "Name of the deal"
                                },
                                "amount": {
                                    "type": "string",
                                    "description": "Deal amount (as string, e.g. '10000.00')"
                                },
                                "pipeline": {
                                    "type": "string", 
                                    "description": "Pipeline ID (default: 'default')",
                                    "default": "default"
                                },
                                "dealstage": {
                                    "type": "string",
                                    "description": "Deal stage ID (default: 'appointmentscheduled')",
                                    "default": "appointmentscheduled"
                                }
                            },
                            "required": ["dealname", "amount"]
                        }
                    ),
                    Tool(
                        name="associate_contact_deal",
                        description="Associate a contact with a deal in HubSpot CRM",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "contact_id": {
                                    "type": "string",
                                    "description": "ID of the contact to associate"
                                },
                                "deal_id": {
                                    "type": "string",
                                    "description": "ID of the deal to associate"
                                }
                            },
                            "required": ["contact_id", "deal_id"]
                        }
                    ),
                    Tool(
                        name="get_deal",
                        description="Retrieve a deal with its associations from HubSpot CRM",
                        inputSchema={
                            "type": "object", 
                            "properties": {
                                "deal_id": {
                                    "type": "string",
                                    "description": "ID of the deal to retrieve"
                                },
                                "include_associations": {
                                    "type": "boolean",
                                    "description": "Whether to include associated contacts and companies",
                                    "default": True
                                }
                            },
                            "required": ["deal_id"]
                        }
                    ),
                    Tool(
                        name="get_contact",
                        description="Retrieve a contact from HubSpot CRM",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "contact_id": {
                                    "type": "string",
                                    "description": "ID of the contact to retrieve"
                                }
                            },
                            "required": ["contact_id"]
                        }
                    ),
                    Tool(
                        name="search_contacts",
                        description="Search for contacts in HubSpot CRM",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "email": {
                                    "type": "string",
                                    "description": "Email to search for"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of results to return",
                                    "default": 10
                                }
                            },
                            "required": ["email"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            """Handle tool calls"""
            
            if not self.hubspot_client:
                return CallToolResult(
                    content=[TextContent(type="text", text="HubSpot client not initialized")]
                )
            
            try:
                if request.name == "create_contact":
                    return await self._create_contact(request.arguments)
                elif request.name == "create_deal":
                    return await self._create_deal(request.arguments)
                elif request.name == "associate_contact_deal":
                    return await self._associate_contact_deal(request.arguments)
                elif request.name == "get_deal":
                    return await self._get_deal(request.arguments)
                elif request.name == "get_contact":
                    return await self._get_contact(request.arguments)
                elif request.name == "search_contacts":
                    return await self._search_contacts(request.arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {request.name}")]
                    )
                    
            except Exception as e:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )
    
    async def _create_contact(self, args: Dict[str, Any]) -> CallToolResult:
        """Create a new contact in HubSpot"""
        try:
            properties = {
                "email": args["email"],
                "firstname": args["firstname"], 
                "lastname": args["lastname"]
            }
            
            # Add optional fields
            if "phone" in args:
                properties["phone"] = args["phone"]
            if "company" in args:
                properties["company"] = args["company"]
            
            contact_input = SimplePublicObjectInputForCreate(properties=properties)
            
            api_response = self.hubspot_client.crm.contacts.basic_api.create(
                simple_public_object_input_for_create=contact_input
            )
            
            result = {
                "success": True,
                "contact_id": api_response.id,
                "properties": dict(api_response.properties),
                "message": f"Contact created successfully with ID: {api_response.id}"
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
            
        except ContactsApiException as e:
            error_result = {
                "success": False,
                "error": str(e),
                "message": "Failed to create contact"
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(error_result, indent=2))]
            )
    
    async def _create_deal(self, args: Dict[str, Any]) -> CallToolResult:
        """Create a new deal in HubSpot"""
        try:
            properties = {
                "dealname": args["dealname"],
                "amount": args["amount"],
                "pipeline": args.get("pipeline", "default"),
                "dealstage": args.get("dealstage", "appointmentscheduled")
            }
            
            deal_input = DealInputForCreate(properties=properties)
            
            api_response = self.hubspot_client.crm.deals.basic_api.create(
                simple_public_object_input_for_create=deal_input
            )
            
            result = {
                "success": True,
                "deal_id": api_response.id,
                "properties": dict(api_response.properties),
                "message": f"Deal created successfully with ID: {api_response.id}"
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "message": "Failed to create deal"
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(error_result, indent=2))]
            )
    
    async def _associate_contact_deal(self, args: Dict[str, Any]) -> CallToolResult:
        """Associate a contact with a deal"""
        try:
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
            
            result = self.hubspot_client.crm.associations.batch_api.create(
                from_object_type="contact",
                to_object_type="deal",
                batch_input_public_association=association_input
            )
            
            response = {
                "success": True,
                "contact_id": contact_id,
                "deal_id": deal_id,
                "message": f"Successfully associated contact {contact_id} with deal {deal_id}"
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(response, indent=2))]
            )
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "message": f"Failed to associate contact {args.get('contact_id')} with deal {args.get('deal_id')}"
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(error_result, indent=2))]
            )
    
    async def _get_deal(self, args: Dict[str, Any]) -> CallToolResult:
        """Retrieve a deal with optional associations"""
        try:
            deal_id = args["deal_id"]
            include_associations = args.get("include_associations", True)
            
            associations = ["contacts", "companies"] if include_associations else None
            
            deal = self.hubspot_client.crm.deals.basic_api.get_by_id(
                deal_id,
                properties=["dealname", "amount", "dealstage", "pipeline", "closedate"],
                associations=associations
            )
            
            result = {
                "success": True,
                "deal_id": deal.id,
                "properties": dict(deal.properties),
                "associations": {}
            }
            
            if deal.associations and include_associations:
                for assoc_type, assoc_data in deal.associations.items():
                    result["associations"][assoc_type] = [
                        {"id": item.id, "type": item.type} 
                        for item in assoc_data.results
                    ]
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "message": f"Failed to retrieve deal {args.get('deal_id')}"
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(error_result, indent=2))]
            )
    
    async def _get_contact(self, args: Dict[str, Any]) -> CallToolResult:
        """Retrieve a contact"""
        try:
            contact_id = args["contact_id"]
            
            contact = self.hubspot_client.crm.contacts.basic_api.get_by_id(
                contact_id,
                properties=["email", "firstname", "lastname", "phone", "company"]
            )
            
            result = {
                "success": True,
                "contact_id": contact.id,
                "properties": dict(contact.properties)
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "message": f"Failed to retrieve contact {args.get('contact_id')}"
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(error_result, indent=2))]
            )
    
    async def _search_contacts(self, args: Dict[str, Any]) -> CallToolResult:
        """Search for contacts by email"""
        try:
            email = args["email"]
            limit = args.get("limit", 10)
            
            # Use search API to find contacts
            from hubspot.crm.contacts import PublicObjectSearchRequest, FilterGroup, Filter
            
            search_request = PublicObjectSearchRequest(
                filter_groups=[
                    FilterGroup(
                        filters=[
                            Filter(
                                property_name="email",
                                operator="EQ",
                                value=email
                            )
                        ]
                    )
                ],
                properties=["email", "firstname", "lastname", "phone", "company"],
                limit=limit
            )
            
            search_result = self.hubspot_client.crm.contacts.search_api.do_search(
                public_object_search_request=search_request
            )
            
            contacts = []
            for contact in search_result.results:
                contacts.append({
                    "contact_id": contact.id,
                    "properties": dict(contact.properties)
                })
            
            result = {
                "success": True,
                "total": search_result.total,
                "contacts": contacts
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "message": f"Failed to search contacts for email: {args.get('email')}"
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(error_result, indent=2))]
            )

def main():
    """Run the HubSpot MCP server"""
    import asyncio
    
    server = HubSpotMCPServer()
    
    async def run_server():
        # Run the MCP server
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await server.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="hubspot-crm",
                    server_version="1.0.0",
                    capabilities=server.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
    
    asyncio.run(run_server())

if __name__ == "__main__":
    main()
