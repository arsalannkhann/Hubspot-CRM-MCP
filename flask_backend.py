#!/usr/bin/env python3
"""
Production-ready Flask backend exposing REST endpoints for business tools.

- Loads .env configuration via python-dotenv
- Uses logging (INFO level)
- Standardized JSON error responses
- Wraps existing async MCP tool handlers (from business_tools_mcp.py)
- Each route parses JSON, invokes async handler with asyncio.run(), and returns JSON

Run:
  python3 flask_backend.py

"""

import os
import json
import logging
import asyncio
from typing import Any, Dict, Optional, Tuple

from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flask_backend")

# Import existing async tool handlers from MCP server
# Importing this module will also initialize any configured clients (Stripe, Twilio, etc.)
from business_tools_mcp import (
    web_search_tool,
    database_query_tool,
    crm_operation_tool,
    enrich_data_tool,
    calendar_operation_tool,
    twilio_communication_tool,
    send_email_tool,
    stripe_operation_tool,
    docs_operation_tool,
    social_media_post_tool,
)

app = Flask(__name__)


def _parse_tool_response(tool_name: str, result_list: Any) -> Tuple[Dict[str, Any], int]:
    """
    Convert MCP tool response (List[types.TextContent]) into (json_dict, http_status).
    The tool returns a list with a single TextContent whose `text` is a JSON string.
    """
    try:
        if not isinstance(result_list, (list, tuple)) or len(result_list) == 0:
            logger.error("%s returned empty response list", tool_name)
            return {"success": False, "error": f"{tool_name} returned empty response"}, 500

        first = result_list[0]
        # TextContent in mcp.types has attribute `.text`
        text_payload = getattr(first, "text", None)
        if not text_payload:
            logger.error("%s response missing text payload", tool_name)
            return {"success": False, "error": f"{tool_name} response missing text"}, 500

        data = json.loads(text_payload)
        # Normalization: ensure success flag exists
        if isinstance(data, dict):
            if "error" in data and not data.get("success"):
                # Treat as client error unless clearly server-side; default 400
                return {"success": False, **data}, 400
            return data, 200
        else:
            return {"success": True, "data": data}, 200
    except json.JSONDecodeError as e:
        logger.exception("%s returned invalid JSON text: %s", tool_name, e)
        return {"success": False, "error": f"Invalid JSON from {tool_name}: {str(e)}"}, 500
    except Exception as e:
        logger.exception("Failed to parse tool response for %s: %s", tool_name, e)
        return {"success": False, "error": f"Failed to parse response: {str(e)}"}, 500


def _json_body_or_error(endpoint: str) -> Optional[Dict[str, Any]]:
    """Safely parse JSON body and return dict or None if error already sent."""
    if not request.is_json:
        return None
    try:
        body: Dict[str, Any] = request.get_json(force=True, silent=False)
        if not isinstance(body, dict):
            return None
        return body
    except Exception as e:
        logger.warning("%s: invalid JSON body: %s", endpoint, e)
        return None


def _error_response(message: str, status: int = 400, endpoint: Optional[str] = None):
    payload = {"success": False, "error": message}
    if endpoint:
        payload["endpoint"] = endpoint
    return jsonify(payload), status


# Health & readiness
@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


# 1) /web_search → POST {query, num_results, search_type}
@app.post("/web_search")
def web_search():
    endpoint = "/web_search"
    body = _json_body_or_error(endpoint)
    if body is None:
        return _error_response("Invalid or missing JSON body", 400, endpoint)
    try:
        res = asyncio.run(web_search_tool(body))
        data, status = _parse_tool_response("web_search", res)
        return jsonify(data), status
    except Exception as e:
        logger.exception("%s failed: %s", endpoint, e)
        return _error_response(f"web_search failed: {str(e)}", 500, endpoint)


# 2) /database_query → POST {query, database, collection, filter, document, update, options}
@app.post("/database_query")
def database_query():
    endpoint = "/database_query"
    body = _json_body_or_error(endpoint)
    if body is None:
        return _error_response("Invalid or missing JSON body", 400, endpoint)
    try:
        res = asyncio.run(database_query_tool(body))
        data, status = _parse_tool_response("database_query", res)
        return jsonify(data), status
    except Exception as e:
        logger.exception("%s failed: %s", endpoint, e)
        return _error_response(f"database_query failed: {str(e)}", 500, endpoint)


# 3) /crm_operation → POST {crm, operation, data}
@app.post("/crm_operation")
def crm_operation():
    endpoint = "/crm_operation"
    body = _json_body_or_error(endpoint)
    if body is None:
        return _error_response("Invalid or missing JSON body", 400, endpoint)
    try:
        res = asyncio.run(crm_operation_tool(body))
        data, status = _parse_tool_response("crm_operation", res)
        return jsonify(data), status
    except Exception as e:
        logger.exception("%s failed: %s", endpoint, e)
        return _error_response(f"crm_operation failed: {str(e)}", 500, endpoint)


# 4) /enrich_data → POST {provider, type, identifier}
@app.post("/enrich_data")
def enrich_data():
    endpoint = "/enrich_data"
    body = _json_body_or_error(endpoint)
    if body is None:
        return _error_response("Invalid or missing JSON body", 400, endpoint)
    try:
        res = asyncio.run(enrich_data_tool(body))
        data, status = _parse_tool_response("enrich_data", res)
        return jsonify(data), status
    except Exception as e:
        logger.exception("%s failed: %s", endpoint, e)
        return _error_response(f"enrich_data failed: {str(e)}", 500, endpoint)


# 5) /calendar_operation → POST {provider, action, data}
@app.post("/calendar_operation")
def calendar_operation():
    endpoint = "/calendar_operation"
    body = _json_body_or_error(endpoint)
    if body is None:
        return _error_response("Invalid or missing JSON body", 400, endpoint)
    try:
        res = asyncio.run(calendar_operation_tool(body))
        data, status = _parse_tool_response("calendar_operation", res)
        return jsonify(data), status
    except Exception as e:
        logger.exception("%s failed: %s", endpoint, e)
        return _error_response(f"calendar_operation failed: {str(e)}", 500, endpoint)


# 6) /twilio_communication → POST {channel, to, from, message, url}
@app.post("/twilio_communication")
def twilio_communication():
    endpoint = "/twilio_communication"
    body = _json_body_or_error(endpoint)
    if body is None:
        return _error_response("Invalid or missing JSON body", 400, endpoint)
    try:
        res = asyncio.run(twilio_communication_tool(body))
        data, status = _parse_tool_response("twilio_communication", res)
        return jsonify(data), status
    except Exception as e:
        logger.exception("%s failed: %s", endpoint, e)
        return _error_response(f"twilio_communication failed: {str(e)}", 500, endpoint)


# 7) /send_email → POST {provider, to, from, subject, body, template_id}
@app.post("/send_email")
def send_email():
    endpoint = "/send_email"
    body = _json_body_or_error(endpoint)
    if body is None:
        return _error_response("Invalid or missing JSON body", 400, endpoint)
    try:
        res = asyncio.run(send_email_tool(body))
        data, status = _parse_tool_response("send_email", res)
        return jsonify(data), status
    except Exception as e:
        logger.exception("%s failed: %s", endpoint, e)
        return _error_response(f"send_email failed: {str(e)}", 500, endpoint)


# 8) /stripe_operation → POST {operation, data}
@app.post("/stripe_operation")
def stripe_operation():
    endpoint = "/stripe_operation"
    body = _json_body_or_error(endpoint)
    if body is None:
        return _error_response("Invalid or missing JSON body", 400, endpoint)
    try:
        res = asyncio.run(stripe_operation_tool(body))
        data, status = _parse_tool_response("stripe_operation", res)
        return jsonify(data), status
    except Exception as e:
        logger.exception("%s failed: %s", endpoint, e)
        return _error_response(f"stripe_operation failed: {str(e)}", 500, endpoint)


# 9) /docs_operation → POST {provider, action, data}
@app.post("/docs_operation")
def docs_operation():
    endpoint = "/docs_operation"
    body = _json_body_or_error(endpoint)
    if body is None:
        return _error_response("Invalid or missing JSON body", 400, endpoint)
    try:
        res = asyncio.run(docs_operation_tool(body))
        data, status = _parse_tool_response("docs_operation", res)
        return jsonify(data), status
    except Exception as e:
        logger.exception("%s failed: %s", endpoint, e)
        return _error_response(f"docs_operation failed: {str(e)}", 500, endpoint)


# 10) /social_media_post → POST {platform, content, media, dry_run}
@app.post("/social_media_post")
def social_media_post():
    endpoint = "/social_media_post"
    body = _json_body_or_error(endpoint)
    if body is None:
        return _error_response("Invalid or missing JSON body", 400, endpoint)
    try:
        res = asyncio.run(social_media_post_tool(body))
        data, status = _parse_tool_response("social_media_post", res)
        return jsonify(data), status
    except Exception as e:
        logger.exception("%s failed: %s", endpoint, e)
        return _error_response(f"social_media_post failed: {str(e)}", 500, endpoint)


# Standardized error handlers
@app.errorhandler(400)
def handle_400(e):
    return jsonify({"success": False, "error": "Bad Request"}), 400


@app.errorhandler(404)
def handle_404(e):
    return jsonify({"success": False, "error": "Not Found"}), 404


@app.errorhandler(500)
def handle_500(e):
    # Do not leak internal details
    return jsonify({"success": False, "error": "Internal Server Error"}), 500


if __name__ == "__main__":
    # Host/port configurable by env, default 0.0.0.0:5000
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    try:
        port = int(os.getenv("FLASK_PORT", "5000"))
    except ValueError:
        port = 5000

    logger.info("Starting Flask backend on %s:%d", host, port)
    # Note: Debug should be controlled via FLASK_ENV; default to False here
    app.run(host=host, port=port, debug=False)

