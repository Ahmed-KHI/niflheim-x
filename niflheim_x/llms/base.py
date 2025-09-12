"""
Base class for LLM adapters.

This module defines the abstract interface that all LLM adapters must implement.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, List, Optional

from ..core.types import Message, AgentResponse, LLMConfig, StreamingToken


class LLMAdapter(ABC):
    """Abstract base class for LLM adapters.
    
    All LLM adapters (OpenAI, Anthropic, etc.) must inherit from this class
    and implement the required methods.
    """
    
    def __init__(self, config: LLMConfig):
        """Initialize the LLM adapter.
        
        Args:
            config: Configuration for the LLM
        """
        self.config = config
    
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        stream: bool = False,
    ) -> AgentResponse:
        """Generate a response from the LLM.
        
        Args:
            messages: List of conversation messages
            tools: Available tools for the LLM to call
            stream: Whether to stream the response
            
        Returns:
            Response from the LLM
        """
        pass
    
    @abstractmethod
    async def stream_response(
        self,
        messages: List[Message], 
        tools: Optional[List[Dict]] = None,
    ) -> AsyncIterator[StreamingToken]:
        """Stream tokens from the LLM response.
        
        Args:
            messages: List of conversation messages
            tools: Available tools for the LLM to call
            
        Yields:
            Individual tokens from the response
        """
        pass
    
    async def validate_connection(self) -> bool:
        """Validate that the LLM connection is working.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            from ..core.types import MessageRole
            test_messages = [Message(role=MessageRole.USER, content="Hello")]
            response = await self.generate_response(test_messages)
            return response.content is not None
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model": self.config.model,
            "provider": self.__class__.__name__.replace("Adapter", "").lower(),
        }
