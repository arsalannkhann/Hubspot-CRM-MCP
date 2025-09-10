#!/usr/bin/env python3
"""
Business Tools MCP Server - Production-Ready Implementation
A complete MCP server providing 10 essential business tools with full error handling.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import logging
from urllib.parse import quote
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from dotenv import load_dotenv
import signal # Import signal module

# Third-party imports for integrations
import aiohttp
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import stripe
from twilio.rest import Client as TwilioClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from hubspot import HubSpot
from simple_salesforce import Salesforce
from notion_client import AsyncClient as NotionClient
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from O365 import Account
import pickle
import tweepy
import pymongo
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
app = Server("business-tools")

# Import configuration with corrected Twilio variable names
from config import (
    SERPAPI_KEY, CLEARBIT_KEY, PEOPLE_DATA_LABS_KEY,
    SENDGRID_KEY, MAILGUN_KEY, STRIPE_KEY,
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER,
    NOTION_KEY, GOOGLE_DRIVE_KEY,
    LINKEDIN_ACCESS_TOKEN, TWITTER_BEARER_TOKEN,
    HUBSPOT_TOKEN, SALESFORCE_TOKEN,
    DATABASE_URL, GOOGLE_CUSTOM_SEARCH_KEY, GOOGLE_CUSTOM_SEARCH_CX,
    OUTLOOK_CLIENT_ID, OUTLOOK_CLIENT_SECRET,
    TWITTER_API_KEY, TWITTER_API_SECRET,
    LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET
)

# ============================================
# ARCHITECTURAL IMPROVEMENTS RECOMMENDATIONS:
# ============================================
# 1. Consider implementing a ConfigManager class for centralized config validation
# 2. Add connection pooling for database connections
# 3. Implement retry logic with exponential backoff for API calls
# 4. Add caching layer for frequently accessed data (Redis/memcached)
# 5. Consider implementing a plugin architecture for easy tool additions
# 6. Add metrics/monitoring support (Prometheus/Grafana)
# 7. Implement rate limiting per API to respect provider limits
# 8. Add webhook support for async operations
# 9. Consider implementing OAuth2 flow for user-specific integrations
# 10. Add data validation using Pydantic models for all tools
# ============================================

# Get Gmail credentials from environment
GMAIL_EMAIL = os.getenv('GMAIL_EMAIL_ADDRESS')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')

# Initialize clients with error handling
try:
    stripe.api_key = STRIPE_KEY if STRIPE_KEY else None
except Exception as e:
    logger.warning(f"Could not initialize Stripe: {e}")
    stripe.api_key = None

try:
    twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN else None
    if twilio_client:
        logger.info(f"Twilio initialized with account SID: {TWILIO_ACCOUNT_SID[:10]}...")
except Exception as e:
    logger.warning(f"Could not initialize Twilio: {e}")
    twilio_client = None

try:
    sendgrid_client = SendGridAPIClient(SENDGRID_KEY) if SENDGRID_KEY else None
except Exception as e:
    logger.warning(f"Could not initialize SendGrid: {e}")
    sendgrid_client = None

try:
    hubspot_client = HubSpot(access_token=HUBSPOT_TOKEN) if HUBSPOT_TOKEN else None
except Exception as e:
    logger.warning(f"Could not initialize HubSpot: {e}")
    hubspot_client = None

try:
    notion_client = NotionClient(auth=NOTION_KEY) if NOTION_KEY else None
except Exception as e:
    logger.warning(f"Could not initialize Notion: {e}")
    notion_client = None

# MongoDB client
mongo_client = None
if DATABASE_URL and DATABASE_URL.startswith("mongodb"):
    try:
        mongo_client = MongoClient(DATABASE_URL)
        # Test connection
        mongo_client.admin.command('ping')
        logger.info("MongoDB connected successfully")
    except Exception as e:
        logger.warning(f"Could not connect to MongoDB: {e}")
        mongo_client = None

# SQL Database engine (async)
db_engine = None
AsyncSessionLocal = None
if DATABASE_URL and not DATABASE_URL.startswith("mongodb"):
    try:
        # Convert sync URL to async URL for SQL databases
        if DATABASE_URL.startswith("postgresql://"):
            async_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        elif DATABASE_URL.startswith("mysql://"):
            async_url = DATABASE_URL.replace("mysql://", "mysql+aiomysql://")
        elif DATABASE_URL.startswith("sqlite://"):
            async_url = DATABASE_URL  # SQLite works as-is
        else:
            async_url = None
        
        if async_url:
            db_engine = create_async_engine(
                async_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                echo=False
            )
            AsyncSessionLocal = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
            logger.info("SQL database engine initialized")
    except Exception as e:
        logger.warning(f"Could not initialize SQL database engine: {e}")
        db_engine = None

@app.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available business tools"""
    return [
        # 1. Web Search Tool
        types.Tool(
            name="web_search",
            description="Search the web using SerpAPI or Google Custom Search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "num_results": {"type": "integer", "description": "Number of results", "default": 10},
                    "search_type": {"type": "string", "enum": ["web", "news", "images"], "default": "web"}
                },
                "required": ["query"]
            }
        ),
        
        # 2. Database Query Tool
        types.Tool(
            name="database_query",
            description="Query custom database (MongoDB/Postgres/MySQL/SQLite)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query for SQL DBs or operation type for MongoDB (find/insert/update/delete)"},
                    "database": {"type": "string", "description": "Database name", "default": "default"},
                    "collection": {"type": "string", "description": "MongoDB collection name (required for MongoDB)"},
                    "filter": {"type": "object", "description": "MongoDB filter/query document (JSON)"},
                    "document": {"type": "object", "description": "MongoDB document for insert/update operations"},
                    "update": {"type": "object", "description": "MongoDB update document"},
                    "options": {"type": "object", "description": "MongoDB operation options (limit, sort, projection, etc.)"},
                    "timeout": {"type": "integer", "description": "Query timeout in seconds", "default": 30}
                },
                "required": ["query"]
            }
        ),
        
        # 3. CRM Integration Tool
        types.Tool(
            name="crm_operation",
            description="Interact with HubSpot or Salesforce CRM",
            inputSchema={
                "type": "object",
                "properties": {
                    "crm": {"type": "string", "enum": ["hubspot", "salesforce"]},
                    "operation": {"type": "string", "enum": ["create_contact", "update_contact", "get_contact", "list_contacts", "create_deal", "get_deals"]},
                    "data": {"type": "object", "description": "Operation-specific data"}
                },
                "required": ["crm", "operation", "data"]
            }
        ),
        
        # 4. Data Enrichment Tool
        types.Tool(
            name="enrich_data",
            description="Enrich contact/company data using Clearbit or People Data Labs",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string", "enum": ["clearbit", "people_data_labs"]},
                    "type": {"type": "string", "enum": ["person", "company"]},
                    "identifier": {"type": "string", "description": "Email for person, domain for company"}
                },
                "required": ["provider", "type", "identifier"]
            }
        ),
        
        # 5. Calendar & Appointment Tool
        types.Tool(
            name="calendar_operation",
            description="Manage calendar and appointments (Google Calendar/Outlook)",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string", "enum": ["google", "outlook"]},
                    "action": {"type": "string", "enum": ["create_event", "get_events", "update_event", "check_availability"]},
                    "data": {"type": "object", "description": "Action-specific data"}
                },
                "required": ["provider", "action"]
            }
        ),
        
        # 6. Twilio Integration Tool
        types.Tool(
            name="twilio_communication",
            description="Send SMS, make calls, or send WhatsApp messages via Twilio",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "enum": ["sms", "voice", "whatsapp"]},
                    "to": {"type": "string", "description": "Recipient phone number"},
                    "from": {"type": "string", "description": "Sender phone number (optional)"},
                    "message": {"type": "string", "description": "Message content (for SMS/WhatsApp)"},
                    "url": {"type": "string", "description": "TwiML URL (for voice calls)"}
                },
                "required": ["channel", "to"]
            }
        ),
        
        # 7. Email Tool
        types.Tool(
            name="send_email",
            description="Send transactional emails via SendGrid, Mailgun, or Gmail SMTP",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string", "enum": ["sendgrid", "mailgun", "gmail"], "default": "sendgrid"},
                    "to": {"type": "array", "items": {"type": "string"}, "description": "Recipient emails"},
                    "from": {"type": "string", "description": "Sender email"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body (HTML supported)"},
                    "template_id": {"type": "string", "description": "Template ID (optional)"}
                },
                "required": ["to", "from", "subject"]
            }
        ),
        
        # 8. Stripe Payment Tool
        types.Tool(
            name="stripe_operation",
            description="Process payments, subscriptions, and invoices via Stripe",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["create_payment", "create_subscription", "create_invoice", "list_customers", "get_balance"]},
                    "data": {"type": "object", "description": "Operation-specific data"}
                },
                "required": ["operation", "data"]
            }
        ),
        
        # 9. Document/Knowledge Base Tool
        types.Tool(
            name="docs_operation",
            description="Interact with Notion or Google Drive for documentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string", "enum": ["notion", "google_drive"]},
                    "action": {"type": "string", "enum": ["search", "create_page", "update_page", "list_pages"]},
                    "data": {"type": "object", "description": "Action-specific data"}
                },
                "required": ["provider", "action", "data"]
            }
        ),
        
        # 10. Social Media Tool
        types.Tool(
            name="social_media_post",
            description="Post to LinkedIn or Twitter/X",
            inputSchema={
                "type": "object",
                "properties": {
                    "platform": {"type": "string", "enum": ["linkedin", "twitter"]},
                    "content": {"type": "string", "description": "Post content"},
                    "media": {"type": "array", "items": {"type": "string"}, "description": "Media URLs (optional)"}
                },
                "required": ["platform", "content"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Route tool calls to appropriate handlers"""
    
    try:
        if name == "web_search":
            return await web_search_tool(arguments)
        elif name == "database_query":
            return await database_query_tool(arguments)
        elif name == "crm_operation":
            return await crm_operation_tool(arguments)
        elif name == "enrich_data":
            return await enrich_data_tool(arguments)
        elif name == "calendar_operation":
            return await calendar_operation_tool(arguments)
        elif name == "twilio_communication":
            return await twilio_communication_tool(arguments)
        elif name == "send_email":
            return await send_email_tool(arguments)
        elif name == "stripe_operation":
            return await stripe_operation_tool(arguments)
        elif name == "docs_operation":
            return await docs_operation_tool(arguments)
        elif name == "social_media_post":
            return await social_media_post_tool(arguments)
        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Unknown tool: {name}",
                    "tool": name
                })
            )]
    except Exception as e:
        logger.error(f"Tool execution failed for {name}: {str(e)}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": f"Tool execution failed: {str(e)}",
                "tool": name
            })
        )]

# Tool 1: Web Search
async def web_search_tool(args: Dict[str, Any]) -> List[types.TextContent]:
    """Search the web using SerpAPI or Google Custom Search"""
    query = args.get("query")
    num_results = args.get("num_results", 10)
    search_type = args.get("search_type", "web")
    
    if not query:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": "Query is required",
                "tool": "web_search"
            })
        )]
    
    # Try SerpAPI first
    if SERPAPI_KEY and SERPAPI_KEY != "your_serpapi_key_here":
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "q": query,
                    "api_key": SERPAPI_KEY,
                    "num": num_results,
                    "engine": "google"
                }
                
                if search_type == "news":
                    params["tbm"] = "nws"
                elif search_type == "images":
                    params["tbm"] = "isch"
                
                async with session.get("https://serpapi.com/search", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        if search_type == "web" or search_type == "news":
                            organic_results = data.get("organic_results", [])
                            for result in organic_results[:num_results]:
                                results.append({
                                    "title": result.get("title"),
                                    "link": result.get("link"),
                                    "snippet": result.get("snippet")
                                })
                        elif search_type == "images":
                            image_results = data.get("images_results", [])
                            for result in image_results[:num_results]:
                                results.append({
                                    "title": result.get("title"),
                                    "link": result.get("link"),
                                    "thumbnail": result.get("thumbnail"),
                                    "original": result.get("original")
                                })
                        
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({
                                "success": True,
                                "query": query,
                                "results": results,
                                "total": len(results),
                                "provider": "serpapi"
                            })
                        )]
                    elif response.status == 401:
                        logger.warning("SerpAPI authentication failed, falling back to Google Custom Search")
                    else:
                        logger.warning(f"SerpAPI returned status {response.status}")
        except Exception as e:
            logger.warning(f"SerpAPI search failed: {e}, falling back to Google Custom Search")
    
    # Fallback to Google Custom Search
    if GOOGLE_CUSTOM_SEARCH_KEY and GOOGLE_CUSTOM_SEARCH_CX:
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "key": GOOGLE_CUSTOM_SEARCH_KEY,
                    "cx": GOOGLE_CUSTOM_SEARCH_CX,
                    "q": query,
                    "num": min(num_results, 10)  # Google limits to 10
                }
                
                if search_type == "images":
                    params["searchType"] = "image"
                
                async with session.get("https://www.googleapis.com/customsearch/v1", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        items = data.get("items", [])
                        for item in items:
                            if search_type == "images":
                                results.append({
                                    "title": item.get("title"),
                                    "link": item.get("link"),
                                    "thumbnail": item.get("image", {}).get("thumbnailLink"),
                                    "context": item.get("image", {}).get("contextLink")
                                })
                            else:
                                results.append({
                                    "title": item.get("title"),
                                    "link": item.get("link"),
                                    "snippet": item.get("snippet")
                                })
                        
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({
                                "success": True,
                                "query": query,
                                "results": results,
                                "total": len(results),
                                "provider": "google_custom_search"
                            })
                        )]
                    else:
                        error_data = await response.text()
                        logger.error(f"Google Custom Search failed: {error_data}")
        except Exception as e:
            logger.error(f"Google Custom Search failed: {e}")
    
    # No search API available
    return [types.TextContent(
        type="text",
        text=json.dumps({
            "error": "No search API configured. Please set SERPAPI_KEY or GOOGLE_CUSTOM_SEARCH_KEY",
            "tool": "web_search"
        })
    )]

# Tool 2: Database Query - Enhanced with full MongoDB support
async def database_query_tool(args: Dict[str, Any]) -> List[types.TextContent]:
    """Query database (MongoDB or SQL) with enhanced MongoDB operations"""
    query = args.get("query", "").lower()
    database = args.get("database", "default")
    collection = args.get("collection")
    filter_doc = args.get("filter", {})
    document = args.get("document", {})
    update_doc = args.get("update", {})
    options = args.get("options", {})
    
    if not query:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": "Query/operation type is required",
                "tool": "database_query",
                "hint": "For MongoDB use: find, insert, update, delete. For SQL use raw SQL query."
            })
        )]
    
    # MongoDB operations
    if mongo_client and (DATABASE_URL and DATABASE_URL.startswith("mongodb")):
        if not collection:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": "Collection name is required for MongoDB operations",
                    "tool": "database_query"
                })
            )]
        
        try:
            db = mongo_client[database]
            coll = db[collection]
            
            # FIND operation
            if "find" in query or "select" in query or "get" in query:
                # Apply options
                limit = options.get("limit", 100)
                sort = options.get("sort")
                projection = options.get("projection")
                skip = options.get("skip", 0)
                
                cursor = coll.find(filter_doc)
                
                if projection:
                    cursor = cursor.projection(projection)
                if sort:
                    # Convert sort to list of tuples if dict
                    if isinstance(sort, dict):
                        sort = [(k, v) for k, v in sort.items()]
                    cursor = cursor.sort(sort)
                if skip:
                    cursor = cursor.skip(skip)
                if limit:
                    cursor = cursor.limit(limit)
                
                results = list(cursor)
                
                # Convert ObjectId and other non-serializable types to strings
                for doc in results:
                    for key, value in doc.items():
                        if hasattr(value, '__str__') and not isinstance(value, (str, int, float, bool, list, dict)):
                            doc[key] = str(value)
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "operation": "find",
                        "database": database,
                        "collection": collection,
                        "filter": filter_doc,
                        "results": results,
                        "count": len(results),
                        "total_count": coll.count_documents(filter_doc)
                    })
                )]
            
            # INSERT operation
            elif "insert" in query or "create" in query or "add" in query:
                if not document:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "Document is required for insert operation",
                            "tool": "database_query"
                        })
                    )]
                
                # Support both single and multiple inserts
                if isinstance(document, list):
                    result = coll.insert_many(document)
                    inserted_ids = [str(id) for id in result.inserted_ids]
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "operation": "insert_many",
                            "database": database,
                            "collection": collection,
                            "inserted_ids": inserted_ids,
                            "inserted_count": len(inserted_ids)
                        })
                    )]
                else:
                    result = coll.insert_one(document)
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "operation": "insert_one",
                            "database": database,
                            "collection": collection,
                            "inserted_id": str(result.inserted_id)
                        })
                    )]
            
            # UPDATE operation
            elif "update" in query or "modify" in query:
                if not update_doc:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "Update document is required for update operation",
                            "tool": "database_query"
                        })
                    )]
                
                # Determine if updating one or many
                if "many" in query or options.get("multi"):
                    result = coll.update_many(filter_doc, update_doc, upsert=options.get("upsert", False))
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "operation": "update_many",
                            "database": database,
                            "collection": collection,
                            "matched_count": result.matched_count,
                            "modified_count": result.modified_count,
                            "upserted_id": str(result.upserted_id) if result.upserted_id else None
                        })
                    )]
                else:
                    result = coll.update_one(filter_doc, update_doc, upsert=options.get("upsert", False))
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "operation": "update_one",
                            "database": database,
                            "collection": collection,
                            "matched_count": result.matched_count,
                            "modified_count": result.modified_count,
                            "upserted_id": str(result.upserted_id) if result.upserted_id else None
                        })
                    )]
            
            # DELETE operation
            elif "delete" in query or "remove" in query:
                # Determine if deleting one or many
                if "many" in query or "all" in query or options.get("multi"):
                    result = coll.delete_many(filter_doc)
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "operation": "delete_many",
                            "database": database,
                            "collection": collection,
                            "deleted_count": result.deleted_count
                        })
                    )]
                else:
                    result = coll.delete_one(filter_doc)
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "operation": "delete_one",
                            "database": database,
                            "collection": collection,
                            "deleted_count": result.deleted_count
                        })
                    )]
            
            # AGGREGATE operation
            elif "aggregate" in query:
                pipeline = filter_doc if isinstance(filter_doc, list) else [filter_doc]
                results = list(coll.aggregate(pipeline))
                
                # Convert non-serializable types
                for doc in results:
                    for key, value in doc.items():
                        if hasattr(value, '__str__') and not isinstance(value, (str, int, float, bool, list, dict)):
                            doc[key] = str(value)
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "operation": "aggregate",
                        "database": database,
                        "collection": collection,
                        "pipeline": pipeline,
                        "results": results,
                        "count": len(results)
                    })
                )]
            
            # COUNT operation
            elif "count" in query:
                count = coll.count_documents(filter_doc)
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "operation": "count",
                        "database": database,
                        "collection": collection,
                        "filter": filter_doc,
                        "count": count
                    })
                )]
            
            # DISTINCT operation
            elif "distinct" in query:
                field = options.get("field") or options.get("key")
                if not field:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "Field name is required for distinct operation (use options.field)",
                            "tool": "database_query"
                        })
                    )]
                
                values = coll.distinct(field, filter_doc)
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "operation": "distinct",
                        "database": database,
                        "collection": collection,
                        "field": field,
                        "values": values,
                        "count": len(values)
                    })
                )]
            
            else:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Unsupported MongoDB operation: {query}",
                        "tool": "database_query",
                        "supported_operations": ["find", "insert", "update", "delete", "aggregate", "count", "distinct"]
                    })
                )]
            
        except Exception as e:
            logger.error(f"MongoDB operation failed: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"MongoDB operation failed: {str(e)}",
                    "tool": "database_query",
                    "operation": query,
                    "database": database,
                    "collection": collection
                })
            )]
    
    # SQL query
    elif db_engine:
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(text(query))
                
                # Handle different result types
                if result.returns_rows:
                    rows = result.fetchall()
                    # Convert rows to dictionaries
                    results = []
                    for row in rows:
                        if hasattr(row, '_mapping'):
                            results.append(dict(row._mapping))
                        else:
                            results.append(dict(zip(result.keys(), row)))
                    
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "database": database,
                            "results": results,
                            "count": len(results)
                        })
                    )]
                else:
                    # For INSERT, UPDATE, DELETE
                    await session.commit()
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "database": database,
                            "rows_affected": result.rowcount
                        })
                    )]
                    
        except Exception as e:
            logger.error(f"SQL query failed: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"SQL query failed: {str(e)}",
                    "tool": "database_query"
                })
            )]
    
    return [types.TextContent(
        type="text",
        text=json.dumps({
            "error": "Database not configured. Please set DATABASE_URL",
            "tool": "database_query"
        })
    )]

# Tool 3: CRM Operations
async def crm_operation_tool(args: Dict[str, Any]) -> List[types.TextContent]:
    """Perform CRM operations on HubSpot or Salesforce"""
    crm = args.get("crm")
    operation = args.get("operation")
    data = args.get("data", {})
    
    if not crm or not operation or not data:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": "CRM, operation, and data are required",
                "tool": "crm_operation"
            })
        )]
    
    if crm == "hubspot":
        if not hubspot_client:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": "HubSpot not configured. Please set HUBSPOT_TOKEN",
                    "tool": "crm_operation"
                })
            )]
        
        try:
            if operation == "create_contact":
                properties = data.get("properties", {})
                response = hubspot_client.crm.contacts.basic_api.create(
                    simple_public_object_input_for_create={"properties": properties}
                )
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "crm": "hubspot",
                        "operation": operation,
                        "contact_id": response.id,
                        "properties": response.properties
                    })
                )]
            
            elif operation == "get_contact":
                contact_id = data.get("id") or data.get("contact_id")
                email = data.get("email")
                
                if email and not contact_id:
                    # Search by email
                    search_response = hubspot_client.crm.contacts.search_api.do_search(
                        public_object_search_request={
                            "filterGroups": [{
                                "filters": [{
                                    "propertyName": "email",
                                    "operator": "EQ",
                                    "value": email
                                }]
                            }]
                        }
                    )
                    if search_response.results:
                        contact = search_response.results[0]
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({
                                "success": True,
                                "crm": "hubspot",
                                "operation": operation,
                                "contact": {
                                    "id": contact.id,
                                    "properties": contact.properties
                                }
                            })
                        )]
                    else:
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({
                                "success": False,
                                "crm": "hubspot",
                                "operation": operation,
                                "error": f"No contact found with email: {email}"
                            })
                        )]
                
                elif contact_id:
                    # Validate contact_id format
                    try:
                        contact_id = str(contact_id)
                        response = hubspot_client.crm.contacts.basic_api.get_by_id(
                            contact_id=contact_id
                        )
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({
                                "success": True,
                                "crm": "hubspot",
                                "operation": operation,
                                "contact": {
                                    "id": response.id,
                                    "properties": response.properties
                                }
                            })
                        )]
                    except Exception as e:
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({
                                "success": False,
                                "crm": "hubspot",
                                "operation": operation,
                                "error": f"Invalid contact ID '{contact_id}'. HubSpot contact IDs should be numeric."
                            })
                        )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "Either contact_id or email is required for get_contact",
                            "tool": "crm_operation"
                        })
                    )]
            
            elif operation == "list_contacts":
                limit = data.get("limit", 10)
                response = hubspot_client.crm.contacts.basic_api.get_page(limit=limit)
                contacts = []
                for contact in response.results:
                    contacts.append({
                        "id": contact.id,
                        "properties": contact.properties
                    })
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "crm": "hubspot",
                        "operation": operation,
                        "contacts": contacts,
                        "total": len(contacts)
                    })
                )]
            
            elif operation == "create_deal":
                properties = data.get("properties", {})
                response = hubspot_client.crm.deals.basic_api.create(
                    simple_public_object_input_for_create={"properties": properties}
                )
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "crm": "hubspot",
                        "operation": operation,
                        "deal_id": response.id,
                        "properties": response.properties
                    })
                )]
            
            else:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Unsupported HubSpot operation: {operation}",
                        "tool": "crm_operation",
                        "supported_operations": ["create_contact", "get_contact", "list_contacts", "create_deal"]
                    })
                )]
                
        except Exception as e:
            logger.error(f"HubSpot operation failed: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"HubSpot operation failed: {str(e)}",
                    "tool": "crm_operation"
                })
            )]
    
    return [types.TextContent(
        type="text",
        text=json.dumps({
            "error": f"Unsupported CRM: {crm}",
            "tool": "crm_operation"
        })
    )]

# Tool 4: Data Enrichment
async def enrich_data_tool(args: Dict[str, Any]) -> List[types.TextContent]:
    """Enrich person or company data"""
    provider = args.get("provider")
    data_type = args.get("type")
    identifier = args.get("identifier")
    
    if not provider or not data_type or not identifier:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": "Provider, type, and identifier are required",
                "tool": "enrich_data"
            })
        )]
    
    if provider == "clearbit":
        if not CLEARBIT_KEY or CLEARBIT_KEY == "your_clearbit_key_here":
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": "Clearbit not configured. Please set CLEARBIT_API_KEY",
                    "tool": "enrich_data"
                })
            )]
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {CLEARBIT_KEY}"}
                
                if data_type == "person":
                    url = f"https://person-stream.clearbit.com/v2/people/find?email={identifier}"
                else:  # company
                    url = f"https://company-stream.clearbit.com/v2/companies/find?domain={identifier}"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({
                                "success": True,
                                "provider": "clearbit",
                                "type": data_type,
                                "identifier": identifier,
                                "enriched_data": data
                            })
                        )]
                    elif response.status == 404:
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({
                                "success": False,
                                "provider": "clearbit",
                                "type": data_type,
                                "identifier": identifier,
                                "error": "No data found for this identifier"
                            })
                        )]
                    elif response.status == 401:
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({
                                "error": "Clearbit authentication failed. Check your API key.",
                                "tool": "enrich_data"
                            })
                        )]
                    else:
                        error_text = await response.text()
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({
                                "error": f"Clearbit API error: {response.status} - {error_text}",
                                "tool": "enrich_data"
                            })
                        )]
                        
        except Exception as e:
            logger.error(f"Clearbit enrichment failed: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Clearbit enrichment failed: {str(e)}",
                    "tool": "enrich_data"
                })
            )]
    
    elif provider == "people_data_labs":
        if not PEOPLE_DATA_LABS_KEY:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": "People Data Labs not configured. Please set PEOPLE_DATA_LABS_KEY",
                    "tool": "enrich_data"
                })
            )]
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"X-Api-Key": PEOPLE_DATA_LABS_KEY}
                
                if data_type == "person":
                    url = "https://api.peopledatalabs.com/v5/person/enrich"
                    params = {"email": identifier}
                else:  # company
                    url = "https://api.peopledatalabs.com/v5/company/enrich"
                    params = {"website": identifier}
                
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({
                                "success": True,
                                "provider": "people_data_labs",
                                "type": data_type,
                                "identifier": identifier,
                                "enriched_data": data.get("data", data)
                            })
                        )]
                    else:
                        error_data = await response.json()
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({
                                "error": f"People Data Labs error: {error_data.get('error', 'Unknown error')}",
                                "tool": "enrich_data"
                            })
                        )]
                        
        except Exception as e:
            logger.error(f"People Data Labs enrichment failed: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"People Data Labs enrichment failed: {str(e)}",
                    "tool": "enrich_data"
                })
            )]
    
    return [types.TextContent(
        type="text",
        text=json.dumps({
            "error": f"Unsupported provider: {provider}",
            "tool": "enrich_data"
        })
    )]

# Tool 5: Calendar Operations
async def calendar_operation_tool(args: Dict[str, Any]) -> List[types.TextContent]:
    """Manage calendar operations"""
    provider = args.get("provider")
    action = args.get("action")
    data = args.get("data", {})
    
    if not provider or not action:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": "Provider and action are required",
                "tool": "calendar_operation"
            })
        )]
    
    if provider == "google":
        try:
            # Load credentials
            creds = None
            token_file = os.getenv("GOOGLE_CALENDAR_TOKEN", "google_calendar_token.pickle")
            
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "Google Calendar not authenticated. Please run authentication flow.",
                            "tool": "calendar_operation"
                        })
                    )]
            
            service = build('calendar', 'v3', credentials=creds)
            
            if action == "get_events":
                calendar_id = data.get("calendar_id", "primary")
                time_min = data.get("time_min", datetime.utcnow().isoformat() + 'Z')
                max_results = data.get("max_results", 10)
                
                events_result = service.events().list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                events = events_result.get('items', [])
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "events": events,
                        "total": len(events)
                    })
                )]
            
            elif action == "create_event":
                calendar_id = data.get("calendar_id", "primary")
                event = {
                    'summary': data.get('summary', 'New Event'),
                    'description': data.get('description', ''),
                    'start': data.get('start', {
                        'dateTime': (datetime.utcnow() + timedelta(days=1)).isoformat(),
                        'timeZone': 'UTC',
                    }),
                    'end': data.get('end', {
                        'dateTime': (datetime.utcnow() + timedelta(days=1, hours=1)).isoformat(),
                        'timeZone': 'UTC',
                    }),
                    'attendees': data.get('attendees', [])
                }
                
                event = service.events().insert(calendarId=calendar_id, body=event).execute()
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "event_id": event.get('id'),
                        "link": event.get('htmlLink')
                    })
                )]
            
        except Exception as e:
            logger.error(f"Google Calendar operation failed: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Google Calendar operation failed: {str(e)}",
                    "tool": "calendar_operation"
                })
            )]
    
    return [types.TextContent(
        type="text",
        text=json.dumps({
            "error": f"Unsupported provider: {provider}",
            "tool": "calendar_operation"
        })
    )]

# Tool 6: Twilio Communication
async def twilio_communication_tool(args: Dict[str, Any]) -> List[types.TextContent]:
    """Send SMS, WhatsApp, or make calls via Twilio"""
    channel = args.get("channel")
    to_number = args.get("to")
    from_number = args.get("from", TWILIO_PHONE_NUMBER)
    message = args.get("message")
    
    if not channel or not to_number:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": "Channel and recipient are required",
                "tool": "twilio_communication"
            })
        )]
    
    if not twilio_client:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": "Twilio not configured. Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN",
                "tool": "twilio_communication"
            })
        )]
    
    try:
        if channel == "sms":
            if not message:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Message is required for SMS",
                        "tool": "twilio_communication"
                    })
                )]
            
            msg = twilio_client.messages.create(
                body=message,
                from_=from_number,
                to=to_number
            )
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "channel": "sms",
                    "message_sid": msg.sid,
                    "status": msg.status,
                    "to": msg.to,
                    "from": msg.from_
                })
            )]
        
        elif channel == "whatsapp":
            if not message:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Message is required for WhatsApp",
                        "tool": "twilio_communication"
                    })
                )]
            
            # WhatsApp numbers need 'whatsapp:' prefix
            wa_from = f"whatsapp:{from_number}" if not from_number.startswith("whatsapp:") else from_number
            wa_to = f"whatsapp:{to_number}" if not to_number.startswith("whatsapp:") else to_number
            
            msg = twilio_client.messages.create(
                body=message,
                from_=wa_from,
                to=wa_to
            )
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "channel": "whatsapp",
                    "message_sid": msg.sid,
                    "status": msg.status,
                    "to": msg.to,
                    "from": msg.from_
                })
            )]
        
        elif channel == "voice":
            url = args.get("url", "http://demo.twilio.com/docs/voice.xml")
            
            call = twilio_client.calls.create(
                url=url,
                from_=from_number,
                to=to_number
            )
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "channel": "voice",
                    "call_sid": call.sid,
                    "status": call.status,
                    "to": call.to,
                    "from": call.from_
                })
            )]
        
    except Exception as e:
        logger.error(f"Twilio communication failed: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": f"Twilio communication failed: {str(e)}",
                "tool": "twilio_communication"
            })
        )]

# Tool 7: Email Services
async def send_email_tool(args: Dict[str, Any]) -> List[types.TextContent]:
    """Send email via SendGrid, Mailgun, or Gmail SMTP"""
    provider = args.get("provider", "sendgrid")
    to_emails = args.get("to", [])
    from_email = args.get("from")
    subject = args.get("subject")
    body = args.get("body", "")
    
    if not to_emails or not from_email or not subject:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": "To, from, and subject are required",
                "tool": "send_email"
            })
        )]
    
    # Ensure to_emails is a list
    if isinstance(to_emails, str):
        to_emails = [to_emails]
    
    # Gmail SMTP
    if provider == "gmail":
        if not GMAIL_EMAIL or not GMAIL_APP_PASSWORD:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": "Gmail not configured. Please set GMAIL_EMAIL_ADDRESS and GMAIL_APP_PASSWORD",
                    "tool": "send_email"
                })
            )]
        
        try:
            msg = MIMEMultipart()
            msg['From'] = from_email or GMAIL_EMAIL
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html' if '<' in body else 'plain'))
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
                server.send_message(msg)
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "provider": "gmail",
                    "to": to_emails,
                    "from": from_email or GMAIL_EMAIL,
                    "subject": subject,
                    "status": "sent"
                })
            )]
            
        except Exception as e:
            logger.error(f"Gmail send failed: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Gmail send failed: {str(e)}",
                    "tool": "send_email"
                })
            )]
    
    # SendGrid
    elif provider == "sendgrid":
        if not sendgrid_client:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": "SendGrid not configured. Please set SENDGRID_API_KEY",
                    "tool": "send_email"
                })
            )]
        
        try:
            message = Mail(
                from_email=from_email,
                to_emails=to_emails,
                subject=subject,
                html_content=body
            )
            
            response = sendgrid_client.send(message)
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "provider": "sendgrid",
                    "to": to_emails,
                    "from": from_email,
                    "subject": subject,
                    "status_code": response.status_code,
                    "message_id": response.headers.get('X-Message-Id')
                })
            )]
            
        except Exception as e:
            logger.error(f"SendGrid send failed: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"SendGrid send failed: {str(e)}",
                    "tool": "send_email"
                })
            )]
    
    # Mailgun
    elif provider == "mailgun":
        if not MAILGUN_KEY:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": "Mailgun not configured. Please set MAILGUN_API_KEY",
                    "tool": "send_email"
                })
            )]
        
        # Mailgun implementation would go here
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": "Mailgun provider not yet implemented",
                "tool": "send_email"
            })
        )]
    
    else:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": f"Unsupported email provider: {provider}. Use 'gmail', 'sendgrid', or 'mailgun'",
                "tool": "send_email"
            })
        )]

# Tool 8: Stripe Operations
async def stripe_operation_tool(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle Stripe payment operations"""
    operation = args.get("operation")
    data = args.get("data", {})
    
    if not operation or not data:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": "Operation and data are required",
                "tool": "stripe_operation"
            })
        )]
    
    if not stripe.api_key:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": "Stripe not configured. Please set STRIPE_API_KEY",
                "tool": "stripe_operation"
            })
        )]
    
    try:
        if operation == "create_payment":
            amount = data.get("amount")  # Amount in cents
            currency = data.get("currency", "usd")
            description = data.get("description", "Payment")
            
            if not amount:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Amount is required for payment creation",
                        "tool": "stripe_operation"
                    })
                )]
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                description=description,
                automatic_payment_methods={"enabled": True}
            )
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "operation": "create_payment",
                    "payment_intent_id": payment_intent.id,
                    "client_secret": payment_intent.client_secret,
                    "amount": payment_intent.amount,
                    "currency": payment_intent.currency,
                    "status": payment_intent.status
                })
            )]
        
        elif operation == "create_subscription":
            customer_id = data.get("customer_id")
            price_id = data.get("price_id")
            
            if not customer_id or not price_id:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "customer_id and price_id are required for subscription",
                        "tool": "stripe_operation"
                    })
                )]
            
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}]
            )
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "operation": "create_subscription",
                    "subscription_id": subscription.id,
                    "customer": subscription.customer,
                    "status": subscription.status,
                    "current_period_end": subscription.current_period_end
                })
            )]
        
        elif operation == "create_invoice":
            customer_id = data.get("customer_id")
            amount = data.get("amount")
            description = data.get("description", "Invoice item")
            
            if not customer_id or not amount:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "customer_id and amount are required for invoice",
                        "tool": "stripe_operation"
                    })
                )]
            
            # Create invoice item
            stripe.InvoiceItem.create(
                customer=customer_id,
                amount=amount,
                currency="usd",
                description=description
            )
            
            # Create and finalize invoice
            invoice = stripe.Invoice.create(
                customer=customer_id,
                auto_advance=True
            )
            invoice = stripe.Invoice.finalize_invoice(invoice.id)
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "operation": "create_invoice",
                    "invoice_id": invoice.id,
                    "number": invoice.number,
                    "amount_due": invoice.amount_due,
                    "status": invoice.status,
                    "hosted_invoice_url": invoice.hosted_invoice_url
                })
            )]
        
        elif operation == "list_customers":
            limit = data.get("limit", 10)
            customers = stripe.Customer.list(limit=limit)
            
            customer_list = []
            for customer in customers:
                customer_list.append({
                    "id": customer.id,
                    "email": customer.email,
                    "name": customer.name,
                    "created": customer.created
                })
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "operation": "list_customers",
                    "customers": customer_list,
                    "total": len(customer_list)
                })
            )]
        
        elif operation == "get_balance":
            balance = stripe.Balance.retrieve()
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "operation": "get_balance",
                    "available": balance.available,
                    "pending": balance.pending
                })
            )]
        
        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Unsupported operation: {operation}",
                    "tool": "stripe_operation",
                    "supported_operations": ["create_payment", "create_subscription", "create_invoice", "list_customers", "get_balance"]
                })
            )]
            
    except stripe.error.StripeError as e:
        logger.error(f"Stripe operation failed: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": f"Stripe operation failed: {str(e)}",
                "tool": "stripe_operation"
            })
        )]

# Tool 9: Docs/Knowledge Base Operations
async def docs_operation_tool(args: Dict[str, Any]) -> List[types.TextContent]:
    """Interact with Notion or Google Drive"""
    provider = args.get("provider")
    action = args.get("action")
    data = args.get("data", {})
    
    if not provider or not action or not data:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": "Provider, action, and data are required",
                "tool": "docs_operation"
            })
        )]
    
    if provider == "notion":
        if not notion_client:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": "Notion not configured. Please set NOTION_API_KEY",
                    "tool": "docs_operation"
                })
            )]
        
        try:
            if action == "search":
                query = data.get("query", "")
                
                # Fixed: Removed invalid timestamp parameter
                response = await notion_client.search(
                    query=query,
                    filter={"property": "object", "value": "page"}
                )
                
                results = []
                for page in response.get("results", []):
                    title = "Untitled"
                    if "title" in page.get("properties", {}):
                        title_prop = page["properties"]["title"]
                        if title_prop.get("title"):
                            title = title_prop["title"][0].get("text", {}).get("content", "Untitled")
                    
                    results.append({
                        "id": page["id"],
                        "title": title,
                        "url": page.get("url"),
                        "last_edited": page.get("last_edited_time")
                    })
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "provider": "notion",
                        "action": "search",
                        "query": query,
                        "results": results,
                        "total": len(results)
                    })
                )]
            
            elif action == "list_pages":
                # List all pages in workspace
                response = await notion_client.search(
                    filter={"property": "object", "value": "page"}
                )
                
                pages = []
                for page in response.get("results", []):
                    title = "Untitled"
                    if "title" in page.get("properties", {}):
                        title_prop = page["properties"]["title"]
                        if title_prop.get("title"):
                            title = title_prop["title"][0].get("text", {}).get("content", "Untitled")
                    
                    pages.append({
                        "id": page["id"],
                        "title": title,
                        "url": page.get("url"),
                        "created": page.get("created_time"),
                        "last_edited": page.get("last_edited_time")
                    })
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "provider": "notion",
                        "action": "list_pages",
                        "pages": pages,
                        "total": len(pages)
                    })
                )]
            
            elif action == "create_page":
                parent_id = data.get("parent_id")
                title = data.get("title", "New Page")
                content = data.get("content", "")
                
                if not parent_id:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "parent_id is required to create a page",
                            "tool": "docs_operation"
                        })
                    )]
                
                # Create new page
                new_page = await notion_client.pages.create(
                    parent={"page_id": parent_id} if "-" in parent_id else {"database_id": parent_id},
                    properties={
                        "title": {
                            "title": [
                                {
                                    "text": {
                                        "content": title
                                    }
                                }
                            ]
                        }
                    },
                    children=[
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": content
                                        }
                                    }
                                ]
                            }
                        }
                    ] if content else []
                )
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "provider": "notion",
                        "action": "create_page",
                        "page_id": new_page["id"],
                        "url": new_page.get("url")
                    })
                )]
            
        except Exception as e:
            logger.error(f"Notion operation failed: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Notion operation failed: {str(e)}",
                    "tool": "docs_operation"
                })
            )]
    
    return [types.TextContent(
        type="text",
        text=json.dumps({
            "error": f"Unsupported provider: {provider}",
            "tool": "docs_operation"
        })
    )]

# Tool 10: Social Media Posting (Twitter/X only)
async def social_media_post_tool(args: Dict[str, Any]) -> List[types.TextContent]:
    """Post to Twitter/X social media platform"""
    platform = args.get("platform")
    content = args.get("content")
    dry_run = args.get("dry_run", False)  # For testing without posting
    
    if not platform or not content:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": "Platform and content are required",
                "tool": "social_media_post",
                "supported_platforms": ["twitter", "x"]
            })
        )]
    
    # Only support Twitter/X
    if platform.lower() in ["twitter", "x"]:
        if not TWITTER_BEARER_TOKEN:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": "Twitter not configured. Please set TWITTER_BEARER_TOKEN",
                    "tool": "social_media_post"
                })
            )]
        
        try:
            # Twitter v2 API with enhanced error handling
            client = tweepy.Client(
                bearer_token=TWITTER_BEARER_TOKEN,
                consumer_key=TWITTER_API_KEY if TWITTER_API_KEY else None,
                consumer_secret=TWITTER_API_SECRET if TWITTER_API_SECRET else None,
                wait_on_rate_limit=True
            )
            
            # Dry-run mode for testing
            if args.get("dry_run", False):
                try:
                    user = client.get_me()
                    username = user.data.username if user and user.data and hasattr(user.data, 'username') else None
                except:
                    username = None
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "platform": "twitter",
                        "dry_run": True,
                        "message": "Credentials validated (no post made)",
                        "content_preview": content[:280],
                        "character_count": len(content),
                        "within_limit": len(content) <= 280,
                        "authenticated_user": username if username else "Bearer token authenticated"
                    })
                )]
            
            # Check content length
            if len(content) > 280:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Tweet too long: {len(content)} characters (max 280)",
                        "tool": "social_media_post",
                        "content_preview": content[:280] + "..."
                    })
                )]
            
            # Post tweet
            response = client.create_tweet(text=content)
            
            if response and response.data:
                tweet_id = response.data.get('id')
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "platform": "twitter",
                        "tweet_id": tweet_id,
                        "url": f"https://twitter.com/i/web/status/{tweet_id}",
                        "content": content,
                        "character_count": len(content)
                    })
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Tweet creation failed - no response data",
                        "tool": "social_media_post"
                    })
                )]
            
        except tweepy.errors.Forbidden as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Twitter API forbidden: {str(e)}",
                    "tool": "social_media_post",
                    "hint": "Check app write permissions"
                })
            )]
        except tweepy.errors.Unauthorized as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Twitter authentication failed: {str(e)}",
                    "tool": "social_media_post",
                    "hint": "Check TWITTER_BEARER_TOKEN"
                })
            )]
        except tweepy.errors.TooManyRequests as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Twitter rate limit: {str(e)}",
                    "tool": "social_media_post",
                    "hint": "Wait before retrying"
                })
            )]
        except Exception as e:
            logger.error(f"Twitter post failed: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Twitter post failed: {str(e)}",
                    "tool": "social_media_post"
                })
            )]
    
    else:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": f"Unsupported platform: {platform}",
                "tool": "social_media_post",
                "supported_platforms": ["twitter", "x"],
                "note": "Only Twitter/X is supported. LinkedIn has been removed."
            })
        )]

async def cleanup_clients():
    """Clean up initialized clients"""
    if mongo_client:
        logger.info("Closing MongoDB client...")
        mongo_client.close()
    if db_engine:
        logger.info("Closing SQL database engine...")
        await db_engine.dispose()

async def main():
    """Main function to run the MCP server"""
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("Shutdown signal received. Initiating graceful shutdown...")
        stop_event.set()

    try:
        loop.add_signal_handler(signal.SIGINT, signal_handler)
        loop.add_signal_handler(signal.SIGTERM, signal_handler)
    except NotImplementedError:
        logger.warning("Cannot set signal handlers on this platform.")

    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            server_task = loop.create_task(app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            ))
            await stop_event.wait()
            logger.info("Attempting to gracefully shut down server...")
            await app.shutdown()
            await server_task
    except asyncio.CancelledError:
        logger.info("Server task cancelled.")
    finally:
        await cleanup_clients()
        pending = asyncio.all_tasks(loop=loop)
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
        await loop.shutdown_asyncgens()
        logger.info("Asyncio event loop shutting down.")

if __name__ == "__main__":
    logger.info("Starting Business Tools MCP Server (Production Ready)")
    asyncio.run(main())
