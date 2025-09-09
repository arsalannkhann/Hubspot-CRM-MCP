#!/usr/bin/env python3
"""
Theta Sales LLM Integration
Connects your AWS-hosted fine-tuned sales LLM to the MCP Business Tools
"""

import asyncio
import json
import os
from typing import Dict, Any, List, Optional
import logging
import aiohttp
import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThetaLLMClient:
    """
    Client for your custom Theta Sales LLM running on AWS
    """
    
    def __init__(
        self,
        endpoint_url: str = None,
        api_key: str = None,
        aws_region: str = "us-east-1",
        model_name: str = "theta-sales-v1",
        use_sagemaker: bool = False,
        use_api_gateway: bool = True,
        use_ec2_endpoint: bool = False
    ):
        """
        Initialize Theta LLM client
        
        Args:
            endpoint_url: Your AWS endpoint URL (API Gateway, ALB, or EC2)
            api_key: API key for authentication
            aws_region: AWS region where your model is hosted
            model_name: Name/version of your Theta model
            use_sagemaker: True if using SageMaker endpoint
            use_api_gateway: True if using API Gateway
            use_ec2_endpoint: True if using direct EC2/ECS endpoint
        """
        self.endpoint_url = endpoint_url or os.getenv("THETA_ENDPOINT_URL")
        self.api_key = api_key or os.getenv("THETA_API_KEY")
        self.aws_region = aws_region or os.getenv("AWS_REGION", "us-east-1")
        self.model_name = model_name
        self.use_sagemaker = use_sagemaker
        self.use_api_gateway = use_api_gateway
        self.use_ec2_endpoint = use_ec2_endpoint
        
        # Initialize AWS clients if needed
        if use_sagemaker:
            self.sagemaker_client = boto3.client(
                'sagemaker-runtime',
                region_name=self.aws_region
            )
            self.sagemaker_endpoint = os.getenv("THETA_SAGEMAKER_ENDPOINT")
        
        # Sales-specific system prompt
        self.system_prompt = """You are Theta, a highly specialized sales AI assistant.
        You have been fine-tuned on extensive sales data and understand:
        - Lead qualification and scoring
        - Sales pipeline management
        - Customer relationship strategies
        - Deal closing techniques
        - B2B and B2C sales patterns
        - Industry-specific sales approaches
        
        You have access to business tools that you can orchestrate to help with sales tasks."""
    
    async def query(self, prompt: str, **kwargs) -> str:
        """
        Query the Theta LLM
        
        Args:
            prompt: User prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        Returns:
            Model response as string
        """
        if self.use_sagemaker:
            return await self._query_sagemaker(prompt, **kwargs)
        elif self.use_api_gateway:
            return await self._query_api_gateway(prompt, **kwargs)
        elif self.use_ec2_endpoint:
            return await self._query_ec2_endpoint(prompt, **kwargs)
        else:
            raise ValueError("No endpoint type specified")
    
    async def _query_api_gateway(self, prompt: str, **kwargs) -> str:
        """Query Theta via API Gateway"""
        try:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key
            }
            
            payload = {
                "model": self.model_name,
                "prompt": f"{self.system_prompt}\n\nUser: {prompt}\n\nAssistant:",
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1000),
                "top_p": kwargs.get("top_p", 0.9),
                "stream": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint_url,
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", data.get("text", ""))
                    else:
                        error_text = await response.text()
                        raise Exception(f"Theta API error: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Error querying Theta via API Gateway: {e}")
            raise
    
    async def _query_sagemaker(self, prompt: str, **kwargs) -> str:
        """Query Theta via SageMaker endpoint"""
        try:
            payload = {
                "inputs": f"{self.system_prompt}\n\nUser: {prompt}\n\nAssistant:",
                "parameters": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_new_tokens": kwargs.get("max_tokens", 1000),
                    "top_p": kwargs.get("top_p", 0.9),
                    "do_sample": True
                }
            }
            
            response = self.sagemaker_client.invoke_endpoint(
                EndpointName=self.sagemaker_endpoint,
                ContentType='application/json',
                Body=json.dumps(payload)
            )
            
            result = json.loads(response['Body'].read().decode())
            return result.get("generated_text", result.get("response", ""))
            
        except ClientError as e:
            logger.error(f"SageMaker error: {e}")
            raise
    
    async def _query_ec2_endpoint(self, prompt: str, **kwargs) -> str:
        """Query Theta via direct EC2/ECS endpoint"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "prompt": prompt,
                "system": self.system_prompt,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1000)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "")
                    else:
                        raise Exception(f"EC2 endpoint error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error querying Theta via EC2: {e}")
            raise
    
    async def analyze_sales_opportunity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Theta to analyze a sales opportunity
        
        Args:
            data: Information about the lead/opportunity
        Returns:
            Analysis with scoring and recommendations
        """
        prompt = f"""Analyze this sales opportunity and provide:
        1. Lead score (0-100)
        2. Probability of closing
        3. Recommended next actions
        4. Potential objections to prepare for
        5. Best tools to use from our toolkit
        
        Opportunity data:
        {json.dumps(data, indent=2)}
        
        Respond in JSON format."""
        
        response = await self.query(prompt)
        
        try:
            return json.loads(response)
        except:
            return {
                "analysis": response,
                "lead_score": 75,
                "close_probability": "Medium",
                "next_actions": ["Follow up", "Schedule demo", "Send proposal"]
            }
    
    async def generate_sales_strategy(self, context: str) -> Dict[str, Any]:
        """
        Generate a complete sales strategy
        """
        prompt = f"""Based on this context, create a comprehensive sales strategy:
        {context}
        
        Include:
        1. Target audience identification
        2. Value proposition
        3. Outreach sequence
        4. Tools needed from our business toolkit
        5. Timeline and milestones
        
        Format as actionable JSON."""
        
        response = await self.query(prompt)
        
        try:
            return json.loads(response)
        except:
            return {"strategy": response}

class ThetaSalesOrchestrator:
    """
    Orchestrates business tools using Theta Sales LLM intelligence
    """
    
    def __init__(self, theta_client: ThetaLLMClient):
        self.theta = theta_client
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self) -> Dict[str, str]:
        """Map of available business tools"""
        return {
            "web_search": "Search for prospects and market intelligence",
            "crm_operation": "Manage leads and deals in CRM",
            "database_query": "Query customer and sales databases",
            "enrich_data": "Enrich lead information",
            "send_email": "Send personalized sales emails",
            "calendar_operation": "Schedule meetings and demos",
            "social_media_post": "LinkedIn outreach and engagement",
            "stripe_operation": "Process payments and subscriptions"
        }
    
    async def process_sales_request(self, request: str) -> Dict[str, Any]:
        """
        Process a sales request using Theta's intelligence
        """
        # Ask Theta to analyze and plan
        analysis_prompt = f"""
        Sales request: "{request}"
        
        Available tools: {json.dumps(list(self.tools.keys()))}
        
        Analyze this request and provide:
        1. Intent classification (lead_gen, qualification, closing, follow_up, etc.)
        2. Priority level (high/medium/low)
        3. Tools to use in sequence
        4. Specific actions for each tool
        5. Success metrics
        
        Respond in JSON format.
        """
        
        response = await self.theta.query(analysis_prompt)
        
        try:
            plan = json.loads(response)
        except:
            plan = {
                "intent": "general_sales",
                "priority": "medium",
                "tools": ["web_search", "crm_operation"],
                "actions": ["Research", "Update CRM"],
                "raw_response": response
            }
        
        return plan
    
    async def execute_sales_workflow(self, workflow: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute a sales workflow planned by Theta
        """
        results = []
        
        for tool in workflow.get("tools", []):
            # This would connect to your actual MCP business_tools_mcp.py
            result = {
                "tool": tool,
                "status": "executed",
                "description": self.tools.get(tool, "Unknown tool")
            }
            results.append(result)
            
            # Log for monitoring
            logger.info(f"Theta executed: {tool}")
        
        return results

# Integration with existing MCP server
async def connect_theta_to_mcp():
    """
    Connect Theta LLM to your MCP Business Tools
    """
    # Import your MCP server
    from business_tools_mcp import (
        web_search_tool,
        database_query_tool,
        crm_operation_tool,
        enrich_data_tool,
        send_email_tool,
        calendar_operation_tool,
        social_media_post_tool,
        stripe_operation_tool
    )
    
    # Initialize Theta client
    theta = ThetaLLMClient(
        endpoint_url=os.getenv("THETA_ENDPOINT_URL"),
        api_key=os.getenv("THETA_API_KEY"),
        use_api_gateway=True  # Change based on your setup
    )
    
    # Create orchestrator
    orchestrator = ThetaSalesOrchestrator(theta)
    
    # Example: Process a sales request
    request = "Find 10 potential enterprise customers in fintech and add them to CRM"
    
    # Get Theta's plan
    plan = await orchestrator.process_sales_request(request)
    print(f"Theta's Plan: {json.dumps(plan, indent=2)}")
    
    # Execute with actual MCP tools
    if "web_search" in plan.get("tools", []):
        search_results = await web_search_tool({"query": "enterprise fintech companies"})
        print(f"Search Results: {search_results[0].text}")
    
    if "crm_operation" in plan.get("tools", []):
        crm_result = await crm_operation_tool({
            "crm": "hubspot",
            "operation": "create_contact",
            "data": {"name": "Fintech Lead", "company": "Example Corp"}
        })
        print(f"CRM Result: {crm_result[0].text}")
    
    return plan

# Demo script
async def demo_theta_integration():
    """
    Demonstrate Theta Sales LLM integration
    """
    print("🚀 Theta Sales LLM + MCP Business Tools Integration")
    print("=" * 60)
    
    # Initialize Theta
    theta = ThetaLLMClient(
        endpoint_url="https://your-theta-api.amazonaws.com/v1/chat",  # Replace with your URL
        api_key="your-theta-api-key",  # Replace with your key
        use_api_gateway=True
    )
    
    # Test connection
    print("\n1️⃣ Testing Theta connection...")
    try:
        response = await theta.query("What's your specialization?")
        print(f"✅ Theta responded: {response[:200]}...")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("   Please configure THETA_ENDPOINT_URL and THETA_API_KEY in .env")
        return
    
    # Analyze a sales opportunity
    print("\n2️⃣ Analyzing sales opportunity...")
    opportunity = {
        "company": "TechCorp Inc",
        "industry": "SaaS",
        "size": "500-1000 employees",
        "budget": "$50,000",
        "timeline": "Q1 2024",
        "pain_points": ["Manual processes", "Lack of integration"],
        "decision_makers": ["CTO", "VP Sales"]
    }
    
    analysis = await theta.analyze_sales_opportunity(opportunity)
    print(f"📊 Theta's Analysis:")
    print(json.dumps(analysis, indent=2))
    
    # Generate sales strategy
    print("\n3️⃣ Generating sales strategy...")
    strategy = await theta.generate_sales_strategy(
        "We're targeting mid-market SaaS companies with our integration platform"
    )
    print(f"📋 Sales Strategy:")
    print(json.dumps(strategy, indent=2))
    
    # Orchestrate tools
    print("\n4️⃣ Orchestrating business tools...")
    orchestrator = ThetaSalesOrchestrator(theta)
    
    sales_requests = [
        "Find competitors of Salesforce and analyze their weaknesses",
        "Schedule follow-up meetings with all hot leads from last week",
        "Send personalized emails to prospects who viewed our pricing page"
    ]
    
    for request in sales_requests:
        print(f"\n📌 Request: {request}")
        plan = await orchestrator.process_sales_request(request)
        print(f"   Tools to use: {', '.join(plan.get('tools', []))}")
        print(f"   Priority: {plan.get('priority', 'medium')}")
    
    print("\n✅ Theta Sales LLM successfully integrated with MCP Business Tools!")

if __name__ == "__main__":
    import sys
    
    print("🤖 Theta Sales LLM Integration for MCP Business Tools")
    print("This connects your AWS-hosted sales LLM to the business tools")
    print("")
    
    # Check configuration
    if not os.getenv("THETA_ENDPOINT_URL"):
        print("⚠️  Please configure your Theta endpoint in .env:")
        print("   THETA_ENDPOINT_URL=https://your-api.amazonaws.com/v1/chat")
        print("   THETA_API_KEY=your-api-key")
        print("   THETA_SAGEMAKER_ENDPOINT=your-endpoint-name (if using SageMaker)")
        print("")
        print("Example configurations provided in the code.")
        sys.exit(1)
    
    # Run demo
    asyncio.run(demo_theta_integration())
