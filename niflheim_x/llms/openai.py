"""
OpenAI LLM adapter for GPT models.

This module provides integration with OpenAI's GPT models including
GPT-3.5-turbo, GPT-4, and GPT-4o.
"""

import json
from typing import AsyncIterator, Dict, List, Optional

import httpx

from .base import LLMAdapter
from ..core.types import (
    Message, 
    AgentResponse, 
    LLMConfig, 
    StreamingToken, 
    ToolCall,
    MessageRole
)


class OpenAIAdapter(LLMAdapter):
    """OpenAI LLM adapter for GPT models.
    
    Supports GPT-3.5-turbo, GPT-4, GPT-4o, and other OpenAI models.
    Handles both regular and streaming responses, plus function calling.
    
    Attributes:
        api_key: OpenAI API key
        base_url: Base URL for OpenAI API (default: https://api.openai.com/v1)
        organization: OpenAI organization ID (optional)
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
        organization: Optional[str] = None,
        **config_kwargs
    ):
        """Initialize the OpenAI adapter.
        
        Args:
            api_key: OpenAI API key
            model: Model name (default: "gpt-4o-mini")
            base_url: API base URL (default: OpenAI)
            organization: OpenAI organization ID
            **config_kwargs: Additional LLM config parameters
        """
        config = LLMConfig(model=model, **config_kwargs)
        super().__init__(config)
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.organization = organization
        
        # Set up HTTP client
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        if organization:
            headers["OpenAI-Organization"] = organization
            
        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=httpx.Timeout(60.0)
        )
    
    def _messages_to_openai_format(self, messages: List[Message]) -> List[Dict]:
        """Convert messages to OpenAI API format.
        
        Args:
            messages: List of messages to convert
            
        Returns:
            Messages in OpenAI format
        """
        openai_messages = []
        
        for message in messages:
            openai_message = {
                "role": message.role.value,
                "content": message.content,
            }
            
            # Add name for assistant messages if agent_name is set
            if message.role == MessageRole.ASSISTANT and message.agent_name:
                openai_message["name"] = message.agent_name
                
            openai_messages.append(openai_message)
        
        return openai_messages
    
    def _parse_tool_calls(self, message: Dict) -> List[ToolCall]:
        """Parse tool calls from OpenAI response.
        
        Args:
            message: OpenAI message with tool calls
            
        Returns:
            List of parsed tool calls
        """
        tool_calls = []
        
        if "tool_calls" in message:
            for tool_call in message["tool_calls"]:
                if tool_call["type"] == "function":
                    func = tool_call["function"]
                    tool_calls.append(ToolCall(
                        name=func["name"],
                        arguments=json.loads(func["arguments"]),
                        call_id=tool_call["id"],
                    ))
        
        return tool_calls
    
    async def generate_response(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        stream: bool = False,
    ) -> AgentResponse:
        """Generate a response using OpenAI API.
        
        Args:
            messages: Conversation messages
            tools: Available tools
            stream: Whether to stream the response
            
        Returns:
            Generated response
        """
        if stream:
            # For streaming, collect all tokens first
            content_parts = []
            tool_calls = []
            
            async for token in self.stream_response(messages, tools):
                if token.content:
                    content_parts.append(token.content)
                # Handle tool calls in streaming (simplified for now)
            
            return AgentResponse(
                content="".join(content_parts),
                tool_calls=tool_calls,
            )
        
        # Non-streaming response
        payload = {
            "model": self.config.model,
            "messages": self._messages_to_openai_format(messages),
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
            "frequency_penalty": self.config.frequency_penalty,
            "presence_penalty": self.config.presence_penalty,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            data = await response.json()
            
            message = data["choices"][0]["message"]
            content = message.get("content", "")
            
            # Parse tool calls if present
            tool_calls = self._parse_tool_calls(message)
            
            return AgentResponse(
                content=content,
                tool_calls=tool_calls,
                usage=data.get("usage"),
                finish_reason=data["choices"][0].get("finish_reason", "completed"),
            )
            
        except httpx.HTTPError as e:
            raise RuntimeError(f"OpenAI API error: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {e}")
    
    async def stream_response(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
    ) -> AsyncIterator[StreamingToken]:
        """Stream response tokens from OpenAI API.
        
        Args:
            messages: Conversation messages
            tools: Available tools
            
        Yields:
            Individual response tokens
        """
        payload = {
            "model": self.config.model,
            "messages": self._messages_to_openai_format(messages),
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
            "frequency_penalty": self.config.frequency_penalty,
            "presence_penalty": self.config.presence_penalty,
            "stream": True,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions", 
                json=payload
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            choice = data["choices"][0]
                            delta = choice.get("delta", {})
                            
                            # Handle content tokens
                            if "content" in delta and delta["content"]:
                                yield StreamingToken(
                                    content=delta["content"],
                                    finish_reason=choice.get("finish_reason")
                                )
                            
                            # Handle tool calls (simplified)
                            if "tool_calls" in delta:
                                yield StreamingToken(
                                    content="",
                                    is_tool_call=True,
                                    finish_reason=choice.get("finish_reason")
                                )
                        
                        except json.JSONDecodeError:
                            continue  # Skip invalid JSON lines
        
        except httpx.HTTPError as e:
            raise RuntimeError(f"OpenAI streaming error: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
