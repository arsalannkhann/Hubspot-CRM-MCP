"""
LLM Client Helper
Provides a unified interface for multiple LLM providers.
Allows easy switching between Gemini, Llama3, OpenAI, Claude, etc.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List
import logging
from config import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    GEMINI_API_KEY,
    ANTHROPIC_API_KEY,
    LOCAL_LLM_HOST,
    LOCAL_LLM_MODEL
)

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Unified LLM client that can switch between providers
    """
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize LLM client with specified provider
        Args:
            provider: Override the default provider from config
        """
        self.provider = provider or LLM_PROVIDER
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client based on provider"""
        logger.info(f"Initializing LLM client for provider: {self.provider}")
        
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "gemini":
            self._init_gemini()
        elif self.provider == "claude":
            self._init_claude()
        elif self.provider == "llama3":
            self._init_llama3()
        else:
            logger.warning(f"Unknown provider {self.provider}, using mock client")
            self.client = MockLLMClient()
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            import openai
            if not OPENAI_API_KEY:
                logger.warning("OpenAI API key not configured, using mock client")
                self.client = MockLLMClient()
                return
            
            openai.api_key = OPENAI_API_KEY
            self.client = OpenAIClient()
        except ImportError:
            logger.error("OpenAI library not installed. Run: pip install openai")
            self.client = MockLLMClient()
    
    def _init_gemini(self):
        """Initialize Google Gemini client"""
        try:
            import google.generativeai as genai
            if not GEMINI_API_KEY:
                logger.warning("Gemini API key not configured, using mock client")
                self.client = MockLLMClient()
                return
            
            genai.configure(api_key=GEMINI_API_KEY)
            self.client = GeminiClient()
        except ImportError:
            logger.error("Google Generative AI library not installed. Run: pip install google-generativeai")
            self.client = MockLLMClient()
    
    def _init_claude(self):
        """Initialize Anthropic Claude client"""
        try:
            import anthropic
            if not ANTHROPIC_API_KEY:
                logger.warning("Anthropic API key not configured, using mock client")
                self.client = MockLLMClient()
                return
            
            self.client = ClaudeClient(api_key=ANTHROPIC_API_KEY)
        except ImportError:
            logger.error("Anthropic library not installed. Run: pip install anthropic")
            self.client = MockLLMClient()
    
    def _init_llama3(self):
        """Initialize local Llama3 client (via Ollama or similar)"""
        try:
            import requests
            # Test connection to local LLM server
            response = requests.get(f"{LOCAL_LLM_HOST}/api/tags", timeout=2)
            if response.status_code == 200:
                self.client = Llama3Client(host=LOCAL_LLM_HOST, model=LOCAL_LLM_MODEL)
            else:
                raise Exception("Local LLM server not responding")
        except Exception as e:
            logger.error(f"Failed to connect to local LLM: {e}")
            logger.info("Make sure Ollama is running: ollama serve")
            self.client = MockLLMClient()
    
    async def query(self, prompt: str, **kwargs) -> str:
        """
        Query the LLM with a prompt
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters for the specific LLM
        Returns:
            The LLM's response as a string
        """
        return await self.client.query(prompt, **kwargs)
    
    async def query_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Query the LLM and get structured JSON response
        Args:
            prompt: The prompt to send to the LLM
            schema: Expected JSON schema for response
            **kwargs: Additional parameters
        Returns:
            Parsed JSON response
        """
        return await self.client.query_structured(prompt, schema, **kwargs)
    
    def switch_provider(self, provider: str):
        """
        Switch to a different LLM provider
        Args:
            provider: Name of the provider to switch to
        """
        self.provider = provider
        self._initialize_client()
        logger.info(f"Switched to LLM provider: {provider}")

# ============================================
# LLM CLIENT IMPLEMENTATIONS
# ============================================

class BaseLLMClient:
    """Base class for LLM clients"""
    
    async def query(self, prompt: str, **kwargs) -> str:
        """Query the LLM with a prompt"""
        raise NotImplementedError
    
    async def query_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Query the LLM and get structured JSON response"""
        # Default implementation: query and parse JSON
        response = await self.query(
            prompt + "\n\nRespond with valid JSON matching the expected schema.",
            **kwargs
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response: {response}")
            return {}

class MockLLMClient(BaseLLMClient):
    """Mock LLM client for testing"""
    
    async def query(self, prompt: str, **kwargs) -> str:
        """Return a mock response"""
        return f"Mock response to: {prompt[:100]}..."
    
    async def query_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Return a mock structured response"""
        return {
            "response": "This is a mock structured response",
            "provider": "mock",
            "prompt_preview": prompt[:50]
        }

class OpenAIClient(BaseLLMClient):
    """OpenAI GPT client"""
    
    async def query(self, prompt: str, model: str = "gpt-4", **kwargs) -> str:
        """Query OpenAI GPT"""
        try:
            import openai
            
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI query failed: {e}")
            return f"Error: {str(e)}"

class GeminiClient(BaseLLMClient):
    """Google Gemini client"""
    
    async def query(self, prompt: str, model_name: str = "gemini-1.5-flash", **kwargs) -> str:
        """Query Google Gemini"""
        try:
            import google.generativeai as genai
            
            model = genai.GenerativeModel(model_name)
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                **kwargs
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini query failed: {e}")
            return f"Error: {str(e)}"

class ClaudeClient(BaseLLMClient):
    """Anthropic Claude client"""
    
    def __init__(self, api_key: str):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def query(self, prompt: str, model: str = "claude-3-opus-20240229", **kwargs) -> str:
        """Query Anthropic Claude"""
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 1000),
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude query failed: {e}")
            return f"Error: {str(e)}"

class Llama3Client(BaseLLMClient):
    """Local Llama3 client (via Ollama)"""
    
    def __init__(self, host: str, model: str):
        self.host = host
        self.model = model
    
    async def query(self, prompt: str, **kwargs) -> str:
        """Query local Llama3 model"""
        try:
            import aiohttp
            
            url = f"{self.host}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                **kwargs
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "")
                    else:
                        raise Exception(f"Ollama returned status {response.status}")
        except Exception as e:
            logger.error(f"Llama3 query failed: {e}")
            return f"Error: {str(e)}"

# ============================================
# HELPER FUNCTIONS
# ============================================

def query_llm(prompt: str, provider: Optional[str] = None) -> str:
    """
    Synchronous helper function to query LLM
    Args:
        prompt: The prompt to send to the LLM
        provider: Optional provider override
    Returns:
        The LLM's response
    """
    client = LLMClient(provider)
    return asyncio.run(client.query(prompt))

async def query_llm_async(prompt: str, provider: Optional[str] = None) -> str:
    """
    Asynchronous helper function to query LLM
    Args:
        prompt: The prompt to send to the LLM
        provider: Optional provider override
    Returns:
        The LLM's response
    """
    client = LLMClient(provider)
    return await client.query(prompt)

def analyze_with_llm(data: Any, analysis_type: str = "general") -> Dict[str, Any]:
    """
    Use LLM to analyze data
    Args:
        data: Data to analyze
        analysis_type: Type of analysis to perform
    Returns:
        Analysis results
    """
    prompts = {
        "general": "Analyze the following data and provide insights:",
        "sales": "Analyze this sales data and identify trends and opportunities:",
        "customer": "Analyze this customer data and provide segmentation insights:",
        "financial": "Analyze this financial data and highlight key metrics:"
    }
    
    prompt = f"{prompts.get(analysis_type, prompts['general'])}\n\n{json.dumps(data, indent=2)}"
    
    client = LLMClient()
    response = asyncio.run(client.query(prompt))
    
    return {
        "analysis": response,
        "data_type": analysis_type,
        "provider": client.provider
    }

# ============================================
# TESTING & EXAMPLES
# ============================================

async def test_llm_providers():
    """Test all configured LLM providers"""
    test_prompt = "What is 2+2? Respond with just the number."
    
    providers = ["gemini", "openai", "claude", "llama3", "mock"]
    results = {}
    
    for provider in providers:
        print(f"\nTesting {provider}...")
        client = LLMClient(provider)
        try:
            response = await client.query(test_prompt)
            results[provider] = {
                "success": True,
                "response": response
            }
            print(f"✅ {provider}: {response}")
        except Exception as e:
            results[provider] = {
                "success": False,
                "error": str(e)
            }
            print(f"❌ {provider}: {e}")
    
    return results

if __name__ == "__main__":
    # Test the LLM client
    print("🧪 Testing LLM Client...")
    print("=" * 50)
    
    # Test synchronous query
    response = query_llm("Hello! What LLM are you?")
    print(f"Response: {response}")
    
    # Test all providers
    print("\n🔄 Testing all providers...")
    results = asyncio.run(test_llm_providers())
    
    print("\n📊 Test Results:")
    print(json.dumps(results, indent=2))
