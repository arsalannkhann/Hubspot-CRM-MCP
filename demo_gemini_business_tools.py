#!/usr/bin/env python3
"""
Demo: Gemini AI + Business Tools
Shows how Gemini can orchestrate your business tools
"""

import asyncio
import json
import os
from datetime import datetime

# Configure Gemini
# Load from environment variables (never hardcode API keys!)
from dotenv import load_dotenv
load_dotenv()

# Set LLM provider
os.environ["LLM_PROVIDER"] = "gemini"

# Import Gemini
import google.generativeai as genai

# Configure API with key from .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ GEMINI_API_KEY not found in .env file")
    print("Please add: GEMINI_API_KEY=your-key-here to .env")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

class BusinessAssistant:
    """AI-powered business assistant using Gemini"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.tools = {
            "web_search": self.mock_web_search,
            "crm_operation": self.mock_crm_operation,
            "send_email": self.mock_send_email,
            "calendar_operation": self.mock_calendar_operation,
            "database_query": self.mock_database_query
        }
    
    async def mock_web_search(self, query):
        """Mock web search"""
        return {
            "results": [
                {"title": f"Result for: {query}", "url": "https://example.com", "snippet": "Relevant information..."},
                {"title": f"Another result: {query}", "url": "https://example2.com", "snippet": "More details..."}
            ]
        }
    
    async def mock_crm_operation(self, operation, data):
        """Mock CRM operation"""
        if operation == "create_contact":
            return {"contact_id": "CRM-12345", "status": "created", "data": data}
        return {"status": "success", "operation": operation}
    
    async def mock_send_email(self, to, subject, body):
        """Mock email sending"""
        return {"email_id": "EMAIL-789", "status": "sent", "to": to, "subject": subject}
    
    async def mock_calendar_operation(self, action, data):
        """Mock calendar operation"""
        if action == "create_event":
            return {"event_id": "CAL-456", "status": "scheduled", "event": data}
        return {"status": "success", "action": action}
    
    async def mock_database_query(self, query):
        """Mock database query"""
        return {
            "results": [
                {"id": 1, "name": "John Doe", "email": "john@example.com"},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
            ],
            "count": 2
        }
    
    async def process_request(self, user_request):
        """Process user request using Gemini to orchestrate tools"""
        
        # Ask Gemini to analyze the request and determine which tools to use
        analysis_prompt = f"""
        You are a business assistant with access to these tools:
        - web_search: Search the web for information
        - crm_operation: Create/update CRM contacts and deals
        - send_email: Send emails
        - calendar_operation: Schedule meetings and events
        - database_query: Query customer database
        
        User request: "{user_request}"
        
        Analyze this request and provide a JSON response with:
        1. "intent": What the user wants to achieve
        2. "tools_needed": List of tools to use
        3. "action_plan": Step-by-step plan
        4. "priority": high/medium/low
        
        Respond ONLY with valid JSON.
        """
        
        response = self.model.generate_content(analysis_prompt)
        
        try:
            # Parse Gemini's response
            analysis = json.loads(response.text)
            return analysis
        except:
            # Fallback if JSON parsing fails
            return {
                "intent": user_request,
                "tools_needed": ["web_search"],
                "action_plan": ["Analyze request", "Execute tools", "Return results"],
                "priority": "medium",
                "raw_response": response.text
            }
    
    async def execute_plan(self, analysis):
        """Execute the plan suggested by Gemini"""
        results = []
        
        for tool_name in analysis.get("tools_needed", []):
            if tool_name in self.tools:
                print(f"   🔧 Executing: {tool_name}")
                # Execute mock tool
                if tool_name == "web_search":
                    result = await self.tools[tool_name]("business leads")
                elif tool_name == "crm_operation":
                    result = await self.tools[tool_name]("create_contact", {"name": "New Lead"})
                elif tool_name == "send_email":
                    result = await self.tools[tool_name](["lead@example.com"], "Follow up", "Hello...")
                elif tool_name == "calendar_operation":
                    result = await self.tools[tool_name]("create_event", {"title": "Sales Call"})
                elif tool_name == "database_query":
                    result = await self.tools[tool_name]("SELECT * FROM leads")
                else:
                    result = {"status": "executed", "tool": tool_name}
                
                results.append({"tool": tool_name, "result": result})
        
        return results

async def main():
    """Main demo"""
    print("🚀 Gemini-Powered Business Assistant Demo")
    print("=" * 60)
    print("✅ Using your Gemini API key")
    print("✅ Connected to mock business tools")
    print("=" * 60)
    
    assistant = BusinessAssistant()
    
    # Test scenarios
    test_requests = [
        "Find new potential customers in the tech industry and add them to our CRM",
        "Schedule a meeting with the sales team for next Monday",
        "Send a follow-up email to all leads from last week",
        "Check our database for customers who haven't been contacted in 30 days"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n📌 Scenario {i}: {request}")
        print("-" * 40)
        
        # Get Gemini's analysis
        print("🤖 Asking Gemini to analyze the request...")
        analysis = await assistant.process_request(request)
        
        # Display analysis
        print(f"📊 Gemini's Analysis:")
        print(f"   Intent: {analysis.get('intent', 'Unknown')}")
        print(f"   Priority: {analysis.get('priority', 'medium')}")
        print(f"   Tools needed: {', '.join(analysis.get('tools_needed', []))}")
        
        if analysis.get('action_plan'):
            print(f"   Action plan:")
            for j, step in enumerate(analysis.get('action_plan', []), 1):
                print(f"      {j}. {step}")
        
        # Execute the plan
        print("\n⚡ Executing plan with mock tools...")
        results = await assistant.execute_plan(analysis)
        
        # Show results
        if results:
            print("✅ Execution complete!")
            for result in results:
                print(f"   - {result['tool']}: Success")
        else:
            print("⚠️  No tools were executed")
    
    # Interactive mode
    print("\n" + "=" * 60)
    print("💬 Interactive Mode - Type your business request (or 'quit' to exit)")
    print("=" * 60)
    
    while True:
        user_input = input("\n🎯 Your request: ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        print("\n🤖 Processing with Gemini...")
        analysis = await assistant.process_request(user_input)
        
        print(f"\n📊 Analysis:")
        print(f"   Intent: {analysis.get('intent', 'Unknown')}")
        print(f"   Tools: {', '.join(analysis.get('tools_needed', []))}")
        
        results = await assistant.execute_plan(analysis)
        if results:
            print(f"✅ Executed {len(results)} tool(s) successfully!")
    
    print("\n👋 Thank you for using Gemini Business Assistant!")

if __name__ == "__main__":
    print("🎯 Gemini + Business Tools Integration Demo")
    print("This demonstrates how Gemini AI can orchestrate your business tools")
    print("")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
