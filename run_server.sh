#!/bin/bash

# HubSpot MCP Server Launcher Script

echo "🚀 Starting HubSpot MCP Server..."
echo "=================================="

# Change to script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "hubspot-env" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please add your HubSpot credentials."
    exit 1
fi

# Activate virtual environment and run server
source hubspot-env/bin/activate

echo "✅ Environment activated"
echo "🔑 Loading HubSpot credentials..."
echo "📡 Starting MCP server..."
echo ""
echo "Server ready! Connect your MCP client to this server."
echo "Use Ctrl+C to stop the server."
echo ""

python hubspot_mcp.py
