# Flask Backend for Business Tools MCP

This document explains how to use the production-ready Flask backend that exposes REST endpoints for all 10 business tools.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the Flask server:**
   ```bash
   python3 flask_backend.py
   ```

4. **Test the API:**
   ```bash
   python3 test_flask_backend.py
   ```

The server will start on `http://localhost:5000` by default.

## Available Endpoints

All endpoints accept `POST` requests with JSON payloads and return JSON responses.

### 1. Web Search
**Endpoint:** `POST /web_search`

**Payload:**
```json
{
  "query": "search terms",
  "num_results": 10,
  "search_type": "web"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/web_search \
  -H "Content-Type: application/json" \
  -d '{"query": "Flask Python", "num_results": 5}'
```

### 2. Database Query
**Endpoint:** `POST /database_query`

**Payload:**
```json
{
  "query": "find",
  "database": "mydb",
  "collection": "users",
  "filter": {"status": "active"},
  "options": {"limit": 10}
}
```

### 3. CRM Operation
**Endpoint:** `POST /crm_operation`

**Payload:**
```json
{
  "crm": "hubspot",
  "operation": "list_contacts",
  "data": {"limit": 10}
}
```

### 4. Data Enrichment
**Endpoint:** `POST /enrich_data`

**Payload:**
```json
{
  "provider": "clearbit",
  "type": "person",
  "identifier": "email@example.com"
}
```

### 5. Calendar Operation
**Endpoint:** `POST /calendar_operation`

**Payload:**
```json
{
  "provider": "google",
  "action": "get_events",
  "data": {"max_results": 10}
}
```

### 6. Twilio Communication
**Endpoint:** `POST /twilio_communication`

**Payload:**
```json
{
  "channel": "sms",
  "to": "+1234567890",
  "from": "+0987654321",
  "message": "Hello from Flask API!"
}
```

### 7. Send Email
**Endpoint:** `POST /send_email`

**Payload:**
```json
{
  "provider": "sendgrid",
  "to": ["recipient@example.com"],
  "from": "sender@example.com",
  "subject": "Test Email",
  "body": "Hello from Flask API!"
}
```

### 8. Stripe Operation
**Endpoint:** `POST /stripe_operation`

**Payload:**
```json
{
  "operation": "list_customers",
  "data": {"limit": 10}
}
```

### 9. Docs Operation
**Endpoint:** `POST /docs_operation`

**Payload:**
```json
{
  "provider": "notion",
  "action": "search",
  "data": {"query": "meeting notes"}
}
```

### 10. Social Media Post
**Endpoint:** `POST /social_media_post`

**Payload:**
```json
{
  "platform": "twitter",
  "content": "Hello from Flask API! 🚀",
  "dry_run": true
}
```

## Response Format

All endpoints return JSON responses with the following structure:

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  // Tool-specific fields
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message",
  "endpoint": "/endpoint_name"
}
```

## Configuration

### Environment Variables

The Flask backend uses the same configuration as the MCP server:

- **Flask-specific:**
  - `FLASK_HOST` (default: "0.0.0.0")
  - `FLASK_PORT` (default: "5000")
  - `FLASK_ENV` (development/production)

- **Tool APIs:** Same as MCP server (see `.env.example`)

### Production Deployment

For production deployment:

1. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 flask_backend:app
   ```

2. **Set environment variables:**
   ```bash
   export FLASK_ENV=production
   export FLASK_HOST=0.0.0.0
   export FLASK_PORT=5000
   ```

3. **Use a reverse proxy (nginx):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Error Handling

The Flask backend provides standardized error handling:

- **400 Bad Request:** Invalid JSON or missing required fields
- **404 Not Found:** Invalid endpoint
- **500 Internal Server Error:** Tool execution failures

Error responses include:
- `success: false`
- `error: "descriptive message"`
- `endpoint: "/endpoint_name"` (when applicable)

## Testing

Run the comprehensive test suite:

```bash
# Start the server in one terminal
python3 flask_backend.py

# Run tests in another terminal
python3 test_flask_backend.py
```

The test script covers:
- Health check
- Valid requests to various endpoints
- Error handling (invalid endpoints, malformed JSON)
- Configuration-dependent responses

## Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok"
}
```

Use this for load balancer health checks and monitoring.

## Differences from MCP Server

| Feature | MCP Server | Flask Backend |
|---------|------------|---------------|
| Protocol | JSON-RPC via stdio | HTTP REST |
| Transport | Standard I/O | HTTP over TCP |
| Integration | Claude Desktop, MCP clients | Any HTTP client |
| Deployment | Process spawning | Web server |
| Scaling | Single process | Multi-worker, load balancing |

## Architecture

The Flask backend wraps the existing MCP tool handlers:

```
HTTP Request → Flask Route → asyncio.run(mcp_tool_handler) → JSON Response
```

This design:
- ✅ Reuses all existing MCP tool logic
- ✅ Maintains the same configuration system
- ✅ Provides both MCP and REST interfaces
- ✅ Ensures consistency between protocols

## Security Considerations

For production deployment:

1. **API Keys:** Store in environment variables, not code
2. **HTTPS:** Use SSL/TLS certificates
3. **Authentication:** Add API key or OAuth middleware if needed
4. **Rate Limiting:** Consider adding rate limiting middleware
5. **CORS:** Configure CORS headers if serving web frontends
6. **Input Validation:** All inputs are validated by the MCP tool handlers

## Monitoring

Add monitoring for:
- Request/response times
- Error rates by endpoint
- API key usage
- Tool configuration status

Consider integrating with:
- Prometheus/Grafana for metrics
- Sentry for error tracking
- CloudWatch/DataDog for infrastructure monitoring
