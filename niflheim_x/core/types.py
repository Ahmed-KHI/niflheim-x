"""
Core type definitions for Niflheim_x.

This module contains all the fundamental data structures used throughout the framework.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Enumeration of message roles in a conversation."""
    SYSTEM = "system"
    USER = "user" 
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """Represents a single message in a conversation.
    
    Attributes:
        role: The role of the message sender (system, user, assistant, tool)
        content: The text content of the message
        metadata: Optional metadata dictionary for custom fields
        timestamp: When the message was created
        agent_name: Name of the agent that sent this message (for multi-agent scenarios)
    """
    role: MessageRole
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    agent_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        return {
            "role": self.role.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "agent_name": self.agent_name,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary format."""
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            agent_name=data.get("agent_name"),
        )


@dataclass
class ToolCall:
    """Represents a tool function call.
    
    Attributes:
        name: Name of the tool function
        arguments: Dictionary of arguments to pass to the tool
        call_id: Unique identifier for this tool call
    """
    name: str
    arguments: Dict[str, Any]
    call_id: str = field(default_factory=lambda: f"call_{datetime.now().timestamp()}")


@dataclass
class ToolResult:
    """Represents the result of a tool execution.
    
    Attributes:
        call_id: The ID of the tool call this result corresponds to
        result: The return value from the tool function
        error: Error message if the tool call failed
        execution_time: How long the tool took to execute (in seconds)
    """
    call_id: str
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0


@dataclass 
class AgentResponse:
    """Represents a response from an agent.
    
    Attributes:
        content: The text response from the agent
        tool_calls: List of tool calls the agent wants to make
        metadata: Additional metadata about the response
        usage: Token usage information from the LLM
        finish_reason: Why the response ended (completed, tool_calls, etc.)
    """
    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    usage: Optional[Dict[str, int]] = None
    finish_reason: str = "completed"
    
    @property
    def has_tool_calls(self) -> bool:
        """Check if this response contains tool calls."""
        return len(self.tool_calls) > 0


class StreamingToken(BaseModel):
    """Represents a single token in a streaming response.
    
    Attributes:
        content: The token content
        is_tool_call: Whether this token is part of a tool call
        finish_reason: Reason for finishing (if this is the last token)
    """
    content: str = ""
    is_tool_call: bool = False
    finish_reason: Optional[str] = None


class LLMConfig(BaseModel):
    """Configuration for LLM adapters.
    
    Attributes:
        model: The model name/identifier
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens to generate
        top_p: Nucleus sampling parameter
        frequency_penalty: Frequency penalty for repetition
        presence_penalty: Presence penalty for repetition
        stream: Whether to stream responses
    """
    model: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    stream: bool = False


@dataclass
class AgentConfig:
    """Configuration for Agent instances.
    
    Attributes:
        name: Name of the agent
        system_prompt: System prompt template
        memory_backend: Type of memory backend to use
        max_memory_messages: Maximum messages to keep in memory
        tool_timeout: Timeout for tool execution (seconds)
        enable_streaming: Whether to enable streaming responses
    """
    name: str = "Agent"
    system_prompt: str = "You are a helpful AI assistant."
    memory_backend: str = "dict"  # dict, sqlite, vector
    max_memory_messages: int = 100
    tool_timeout: float = 30.0
    enable_streaming: bool = False


# Type aliases for convenience
MessageList = List[Message]
ToolCallList = List[ToolCall]
ToolResultList = List[ToolResult]
