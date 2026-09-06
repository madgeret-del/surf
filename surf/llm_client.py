"""
LLM Client for Surf AI Agent.

A flexible client that works with any LLM provider via configurable base URL and API key.
Supports OpenAI-compatible APIs as well as custom providers.
"""

import json
import time
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import httpx

from .config import SurfConfig


@dataclass
class Message:
    """Represents a message in a conversation."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Response from the LLM."""
    content: str
    finish_reason: str
    usage: Dict[str, int]
    raw_response: Optional[Dict[str, Any]] = None


class LLMClient:
    """
    Client for interacting with LLM APIs.
    
    Supports both OpenAI-compatible APIs and custom providers.
    Handles authentication, request formatting, and error handling.
    """
    
    def __init__(self, config: SurfConfig):
        """
        Initialize the LLM client with configuration.
        
        Args:
            config: SurfConfig instance with API settings
        """
        self.config = config
        self.client = httpx.Client(timeout=config.timeout)
        self.conversation_history: List[Message] = []
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # Add API key header
        api_key = self.config.api_key
        if api_key:
            # Try Bearer auth first
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Merge custom headers
        headers.update(self.config.headers)
        return headers
    
    def _build_payload(self, messages: List[Message], **kwargs: Any) -> Dict[str, Any]:
        """Build the request payload for the LLM."""
        payload = {
            "model": self.config.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            **self.config.extra_params,
        }
        payload.update(kwargs)
        return payload
    
    def _is_openai_compatible(self) -> bool:
        """Check if the base URL looks like OpenAI-compatible API."""
        return (
            "openai.com" in self.config.base_url or
            "api.openai.com" in self.config.base_url or
            self.config.base_url.endswith("/v1")
        )
    
    def _get_endpoint(self) -> str:
        """Get the appropriate API endpoint."""
        if self._is_openai_compatible():
            return f"{self.config.base_url}/chat/completions"
        # For custom providers, assume they follow OpenAI format
        if self.config.base_url.endswith("/chat/completions"):
            return self.config.base_url
        if self.config.base_url.endswith("/"):
            return f"{self.config.base_url}chat/completions"
        return f"{self.config.base_url}/chat/completions"
    
    async def _make_request_async(self, messages: List[Message], **kwargs: Any) -> LLMResponse:
        """Make an async request to the LLM (for async contexts)."""
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            payload = self._build_payload(messages, **kwargs)
            headers = self._get_headers()
            endpoint = self._get_endpoint()
            
            try:
                response = await client.post(
                    endpoint,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return self._parse_response(data)
            except httpx.HTTPStatusError as e:
                raise ValueError(f"API request failed: {e.response.status_code} - {e.response.text}")
            except httpx.ConnectError as e:
                raise ConnectionError(f"Failed to connect to API: {e}")
            except Exception as e:
                raise ValueError(f"Unexpected error: {e}")
    
    def _make_request(self, messages: List[Message], **kwargs: Any) -> LLMResponse:
        """Make a synchronous request to the LLM."""
        payload = self._build_payload(messages, **kwargs)
        headers = self._get_headers()
        endpoint = self._get_endpoint()
        
        try:
            response = self.client.post(
                endpoint,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return self._parse_response(data)
        except httpx.HTTPStatusError as e:
            raise ValueError(f"API request failed: {e.response.status_code} - {e.response.text}")
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to API: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error: {e}")
    
    def _parse_response(self, data: Dict[str, Any]) -> LLMResponse:
        """Parse the response from the LLM."""
        # Handle OpenAI format
        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            content = choice.get("message", {}).get("content", "")
            finish_reason = choice.get("finish_reason", "stop")
            usage = data.get("usage", {})
            return LLMResponse(
                content=content,
                finish_reason=finish_reason,
                usage=usage,
                raw_response=data
            )
        
        # Handle custom formats - try to extract content
        if "output" in data:
            return LLMResponse(
                content=str(data["output"]),
                finish_reason="stop",
                usage={},
                raw_response=data
            )
        
        if "response" in data:
            return LLMResponse(
                content=str(data["response"]),
                finish_reason="stop",
                usage={},
                raw_response=data
            )
        
        # Fallback
        return LLMResponse(
            content=str(data),
            finish_reason="unknown",
            usage={},
            raw_response=data
        )
    
    def chat(self, messages: List[Message], stream: bool = False, **kwargs: Any) -> LLMResponse:
        """
        Send a chat completion request to the LLM.
        
        Args:
            messages: List of Message objects for the conversation
            stream: Whether to stream the response (not yet implemented)
            **kwargs: Additional parameters for the request
            
        Returns:
            LLMResponse with the generated content
        """
        if stream:
            raise NotImplementedError("Streaming is not yet implemented")
        
        response = self._make_request(messages, **kwargs)
        
        if self.config.verbose:
            print(f"[Surf LLM] Request: {json.dumps(self._build_payload(messages), indent=2)}")
            print(f"[Surf LLM] Response: {response.content[:200]}...")
        
        return response
    
    def complete(self, prompt: str, system: Optional[str] = None, **kwargs: Any) -> str:
        """
        Simple completion interface for single prompts.
        
        Args:
            prompt: User prompt
            system: Optional system message
            **kwargs: Additional parameters
            
        Returns:
            Generated text content
        """
        messages: List[Message] = []
        
        if system:
            messages.append(Message(role="system", content=system))
        
        messages.append(Message(role="user", content=prompt))
        
        response = self.chat(messages, **kwargs)
        return response.content
    
    def add_to_history(self, message: Message) -> None:
        """Add a message to the conversation history."""
        self.conversation_history.append(message)
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
    
    def get_history(self) -> List[Message]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
    
    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # Async context manager
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()
