"""
Anthropic LLM adapter for Claude models.

This module provides integration with Anthropic's Claude models including
Claude 3.5 Sonnet, Claude 3 Haiku, and Claude 3 Opus.
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


class AnthropicAdapter(LLMAdapter):
    """Anthropic LLM adapter for Claude models.
    
    Supports Claude 3.5 Sonnet, Claude 3 Haiku, Claude 3 Opus and other Anthropic models.
    Handles both regular and streaming responses, plus tool usage.
    
    Attributes:
        api_key: Anthropic API key
        base_url: Base URL for Anthropic API (default: https://api.anthropic.com)
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        base_url: str = "https://api.anthropic.com",
        **config_kwargs
    ):
        """Initialize the Anthropic adapter.
        
        Args:
            api_key: Anthropic API key
            model: Model name (default: "claude-3-5-sonnet-20241022")
            base_url: API base URL (default: Anthropic)
            **config_kwargs: Additional LLM config parameters
        """
        config = LLMConfig(model=model, **config_kwargs)
        super().__init__(config)
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        
        # Set up HTTP client
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
            
        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=httpx.Timeout(60.0)
        )
    
    def _messages_to_anthropic_format(self, messages: List[Message]) -> tuple[str, List[Dict]]:
        """Convert messages to Anthropic API format.
        
        Args:
            messages: List of messages to convert
            
        Returns:
            Tuple of (system_prompt, conversation_messages)
        """
        system_prompt = ""
        conversation_messages = []
        
        for message in messages:
            if message.role == MessageRole.SYSTEM:
                system_prompt = message.content
            else:
                conversation_messages.append({
                    "role": "user" if message.role == MessageRole.USER else "assistant",
                    "content": message.content,
                })
        
        return system_prompt, conversation_messages
    
    def _parse_tool_calls(self, content: List[Dict]) -> List[ToolCall]:
        """Parse tool calls from Anthropic response.
        
        Args:
            content: Anthropic response content
            
        Returns:
            List of parsed tool calls
        """
        tool_calls = []
        
        for item in content:
            if item.get("type") == "tool_use":
                tool_calls.append(ToolCall(
                    name=item["name"],
                    arguments=item["input"],
                    call_id=item["id"],
                ))
        
        return tool_calls
    
    async def generate_response(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        stream: bool = False,
    ) -> AgentResponse:
        """Generate a response using Anthropic API.
        
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
        system_prompt, conversation_messages = self._messages_to_anthropic_format(messages)
        
        payload = {
            "model": self.config.model,
            "messages": conversation_messages,
            "max_tokens": self.config.max_tokens or 4096,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        if tools:
            payload["tools"] = tools
        
        try:
            response = await self.client.post(
                f"{self.base_url}/v1/messages",
                json=payload
            )
            response.raise_for_status()
            data = await response.json()
            
            content = data["content"]
            
            # Extract text content
            text_content = ""
            for item in content:
                if item.get("type") == "text":
                    text_content += item["text"]
            
            # Parse tool calls if present
            tool_calls = self._parse_tool_calls(content)
            
            return AgentResponse(
                content=text_content,
                tool_calls=tool_calls,
                usage=data.get("usage"),
                finish_reason=data.get("stop_reason", "completed"),
            )
            
        except httpx.HTTPError as e:
            raise RuntimeError(f"Anthropic API error: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {e}")
    
    async def stream_response(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
    ) -> AsyncIterator[StreamingToken]:
        """Stream response tokens from Anthropic API.
        
        Args:
            messages: Conversation messages
            tools: Available tools
            
        Yields:
            Individual response tokens
        """
        system_prompt, conversation_messages = self._messages_to_anthropic_format(messages)
        
        payload = {
            "model": self.config.model,
            "messages": conversation_messages,
            "max_tokens": self.config.max_tokens or 4096,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "stream": True,
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        if tools:
            payload["tools"] = tools
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/v1/messages", 
                json=payload
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        try:
                            data = json.loads(data_str)
                            
                            if data.get("type") == "content_block_delta":
                                delta = data.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    yield StreamingToken(
                                        content=delta.get("text", "")
                                    )
                            
                            elif data.get("type") == "message_stop":
                                yield StreamingToken(
                                    content="",
                                    finish_reason="completed"
                                )
                        
                        except json.JSONDecodeError:
                            continue  # Skip invalid JSON lines
        
        except httpx.HTTPError as e:
            raise RuntimeError(f"Anthropic streaming error: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
