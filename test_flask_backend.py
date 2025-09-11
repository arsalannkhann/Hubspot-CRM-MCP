#!/usr/bin/env python3
"""
Simple test script for Flask backend endpoints.

Usage:
  1. Start the Flask backend: python3 flask_backend.py
  2. Run this test: python3 test_flask_backend.py

This demonstrates how to call the Flask REST endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    print()

def test_web_search():
    """Test web search endpoint"""
    print("=== Testing Web Search ===")
    payload = {
        "query": "Flask Python web framework",
        "num_results": 5,
        "search_type": "web"
    }
    try:
        response = requests.post(f"{BASE_URL}/web_search", json=payload)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Success: {result.get('success', False)}")
        if result.get('error'):
            print(f"Error: {result['error']}")
        elif result.get('results'):
            print(f"Found {len(result['results'])} results")
    except Exception as e:
        print(f"Web search failed: {e}")
    print()

def test_database_query():
    """Test database query endpoint"""
    print("=== Testing Database Query ===")
    payload = {
        "query": "find",
        "database": "test_db",
        "collection": "test_collection",
        "filter": {"status": "active"},
        "options": {"limit": 10}
    }
    try:
        response = requests.post(f"{BASE_URL}/database_query", json=payload)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Success: {result.get('success', False)}")
        if result.get('error'):
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Database query failed: {e}")
    print()

def test_crm_operation():
    """Test CRM operation endpoint"""
    print("=== Testing CRM Operation ===")
    payload = {
        "crm": "hubspot",
        "operation": "list_contacts",
        "data": {"limit": 5}
    }
    try:
        response = requests.post(f"{BASE_URL}/crm_operation", json=payload)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Success: {result.get('success', False)}")
        if result.get('error'):
            print(f"Error: {result['error']}")
        elif result.get('contacts'):
            print(f"Found {len(result['contacts'])} contacts")
    except Exception as e:
        print(f"CRM operation failed: {e}")
    print()

def test_social_media_post():
    """Test social media post endpoint (dry run)"""
    print("=== Testing Social Media Post (Dry Run) ===")
    payload = {
        "platform": "twitter",
        "content": "Test post from Flask backend! 🚀 #FlaskAPI #MCP",
        "dry_run": True
    }
    try:
        response = requests.post(f"{BASE_URL}/social_media_post", json=payload)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Success: {result.get('success', False)}")
        if result.get('error'):
            print(f"Error: {result['error']}")
        elif result.get('dry_run'):
            print("Dry run successful - credentials validated")
    except Exception as e:
        print(f"Social media post failed: {e}")
    print()

def test_invalid_endpoint():
    """Test invalid endpoint"""
    print("=== Testing Invalid Endpoint ===")
    try:
        response = requests.post(f"{BASE_URL}/nonexistent_endpoint", json={})
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
    except Exception as e:
        print(f"Invalid endpoint test failed: {e}")
    print()

def test_malformed_json():
    """Test malformed JSON"""
    print("=== Testing Malformed JSON ===")
    try:
        response = requests.post(
            f"{BASE_URL}/web_search",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
    except Exception as e:
        print(f"Malformed JSON test failed: {e}")
    print()

def main():
    """Run all tests"""
    print("Flask Backend API Tests")
    print("=" * 50)
    
    # Test health first
    test_health()
    
    # Test various endpoints
    test_web_search()
    test_database_query()
    test_crm_operation()
    test_social_media_post()
    
    # Test error cases
    test_invalid_endpoint()
    test_malformed_json()
    
    print("Tests completed!")

if __name__ == "__main__":
    main()
