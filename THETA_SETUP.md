# Theta Sales LLM Integration Guide

## Overview
This guide explains how to connect your AWS-hosted Theta Sales LLM (fine-tuned on sales data) to the MCP Business Tools server.

## Architecture Options

### Option 1: API Gateway (Recommended)
```
Theta LLM (AWS) → API Gateway → Your App → MCP Tools
```

### Option 2: SageMaker Endpoint
```
Theta LLM (SageMaker) → SageMaker Runtime → Your App → MCP Tools
```

### Option 3: Direct EC2/ECS Endpoint
```
Theta LLM (EC2/ECS) → Load Balancer → Your App → MCP Tools
```

## Setup Steps

### 1. Configure AWS Endpoint

#### For API Gateway:
```bash
# Add to .env file
THETA_ENDPOINT_URL=https://abc123.execute-api.us-east-1.amazonaws.com/prod/chat
THETA_API_KEY=your-api-gateway-key
LLM_PROVIDER=theta
```

#### For SageMaker:
```bash
# Add to .env file
THETA_SAGEMAKER_ENDPOINT=theta-sales-endpoint-2024
AWS_REGION=us-east-1
LLM_PROVIDER=theta
# Configure AWS credentials (AWS CLI or IAM role)
```

#### For EC2/ECS Direct:
```bash
# Add to .env file
THETA_ENDPOINT_URL=https://theta-llm.your-domain.com/api/chat
THETA_API_KEY=your-bearer-token
LLM_PROVIDER=theta
```

### 2. Install Dependencies

```bash
pip install boto3  # For SageMaker
pip install aiohttp  # For async HTTP calls
```

### 3. Test Connection

```python
# Quick test script
from theta_llm_integration import ThetaLLMClient
import asyncio

async def test():
    client = ThetaLLMClient(
        endpoint_url="your-endpoint",
        api_key="your-key",
        use_api_gateway=True
    )
    response = await client.query("What are you specialized in?")
    print(response)

asyncio.run(test())
```

## Integration Patterns

### Pattern 1: Direct Tool Execution
```python
from theta_llm_integration import ThetaLLMClient, ThetaSalesOrchestrator
from business_tools_mcp import web_search_tool, crm_operation_tool

# Initialize Theta
theta = ThetaLLMClient(endpoint_url="...", api_key="...")
orchestrator = ThetaSalesOrchestrator(theta)

# Process sales request
plan = await orchestrator.process_sales_request(
    "Find 10 enterprise leads in fintech"
)

# Execute tools based on Theta's plan
for tool_name in plan["tools"]:
    if tool_name == "web_search":
        results = await web_search_tool({"query": "fintech enterprise"})
```

### Pattern 2: LLM Client Abstraction
```python
from llm_client import LLMClient

# Use Theta through unified interface
client = LLMClient(provider="theta")
response = await client.query("Analyze this sales opportunity...")
```

### Pattern 3: Sales-Specific Workflows
```python
# Theta has specialized methods for sales
opportunity_analysis = await theta.analyze_sales_opportunity({
    "company": "TechCorp",
    "budget": "$100k",
    "timeline": "Q1 2024"
})

strategy = await theta.generate_sales_strategy(
    "B2B SaaS targeting enterprises"
)
```

## API Specifications

### Expected Request Format (API Gateway)
```json
{
  "model": "theta-sales-v1",
  "prompt": "Your prompt here",
  "temperature": 0.7,
  "max_tokens": 1000,
  "top_p": 0.9,
  "stream": false
}
```

### Expected Response Format
```json
{
  "response": "Generated text from Theta",
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 100
  },
  "model": "theta-sales-v1"
}
```

### SageMaker Format
```json
{
  "inputs": "Your prompt here",
  "parameters": {
    "temperature": 0.7,
    "max_new_tokens": 1000,
    "top_p": 0.9,
    "do_sample": true
  }
}
```

## Sales-Specific Features

Theta is optimized for:

1. **Lead Scoring**: Automatically scores leads 0-100
2. **Pipeline Management**: Understands sales stages
3. **Objection Handling**: Predicts and addresses objections
4. **Deal Analysis**: Evaluates deal probability
5. **Tool Selection**: Knows which business tools to use

## Example Use Cases

### 1. Lead Generation Workflow
```python
# Theta analyzes request and selects tools
request = "Find decision makers at Fortune 500 fintech companies"
plan = await orchestrator.process_sales_request(request)
# Plan: web_search → enrich_data → crm_operation
```

### 2. Deal Qualification
```python
opportunity = {
    "company_size": 500,
    "budget": "$50k",
    "timeline": "3 months",
    "pain_points": ["integration", "scalability"]
}
analysis = await theta.analyze_sales_opportunity(opportunity)
# Returns: lead_score, close_probability, next_actions
```

### 3. Automated Follow-ups
```python
request = "Send personalized follow-ups to all leads from webinar"
plan = await orchestrator.process_sales_request(request)
# Plan: database_query → send_email → calendar_operation
```

## Monitoring & Optimization

### CloudWatch Metrics (if using AWS)
- Monitor latency: `p99 < 2 seconds`
- Track token usage for cost optimization
- Set up alarms for error rates

### Performance Tips
1. Use connection pooling for high volume
2. Implement caching for repeated queries
3. Batch requests when possible
4. Use async operations for parallel processing

## Troubleshooting

### Common Issues

1. **Connection Timeout**
   - Increase timeout in aiohttp ClientTimeout
   - Check AWS security groups/NACLs

2. **Authentication Failed**
   - Verify API key in headers
   - Check IAM permissions for SageMaker

3. **Response Format Issues**
   - Theta might need prompt engineering for JSON
   - Add explicit format instructions in prompts

4. **Rate Limiting**
   - Implement exponential backoff
   - Use request queuing

## Security Considerations

1. **API Keys**: Store in environment variables, never commit
2. **Network**: Use VPC endpoints for internal AWS traffic
3. **Data**: Ensure PII is handled according to compliance
4. **Monitoring**: Log requests but redact sensitive data

## Cost Optimization

1. **Caching**: Cache Theta responses for repeated queries
2. **Batching**: Batch similar requests together
3. **Model Selection**: Use smaller model variants for simple tasks
4. **Throttling**: Implement rate limiting to control costs

## Support

For issues with:
- **Theta Model**: Contact your ML team
- **AWS Infrastructure**: Check CloudWatch logs
- **MCP Integration**: See business_tools_mcp.py
- **General Setup**: Refer to this guide

## Next Steps

1. Configure your Theta endpoint in `.env`
2. Test connection with `python theta_llm_integration.py`
3. Start using Theta for sales automation
4. Monitor performance and optimize
