"""
Tests for core types and data structures.
"""

import pytest
from datetime import datetime
from niflheim_x.core.types import (
    Message, 
    MessageRole, 
    ToolCall, 
    ToolResult, 
    AgentResponse,
    LLMConfig,
    AgentConfig
)


class TestMessage:
    """Test Message class functionality."""
    
    def test_message_creation(self):
        """Test basic message creation."""
        message = Message(
            role=MessageRole.USER,
            content="Hello, world!"
        )
        
        assert message.role == MessageRole.USER
        assert message.content == "Hello, world!"
        assert isinstance(message.timestamp, datetime)
        assert message.agent_name is None
        assert message.metadata == {}
    
    def test_message_with_metadata(self):
        """Test message creation with metadata."""
        metadata = {"source": "test", "priority": "high"}
        message = Message(
            role=MessageRole.ASSISTANT,
            content="Test response",
            metadata=metadata,
            agent_name="TestBot"
        )
        
        assert message.metadata == metadata
        assert message.agent_name == "TestBot"
    
    def test_message_to_dict(self):
        """Test message serialization to dictionary."""
        message = Message(
            role=MessageRole.SYSTEM,
            content="System prompt",
            agent_name="System"
        )
        
        data = message.to_dict()
        
        assert data["role"] == "system"
        assert data["content"] == "System prompt"
        assert data["agent_name"] == "System"
        assert "timestamp" in data
        assert "metadata" in data
    
    def test_message_from_dict(self):
        """Test message deserialization from dictionary."""
        data = {
            "role": "user",
            "content": "Test message",
            "metadata": {"test": True},
            "timestamp": "2024-01-01T12:00:00",
            "agent_name": "TestUser"
        }
        
        message = Message.from_dict(data)
        
        assert message.role == MessageRole.USER
        assert message.content == "Test message"
        assert message.metadata == {"test": True}
        assert message.agent_name == "TestUser"


class TestToolCall:
    """Test ToolCall class functionality."""
    
    def test_tool_call_creation(self):
        """Test basic tool call creation."""
        tool_call = ToolCall(
            name="calculator",
            arguments={"expression": "2 + 2"}
        )
        
        assert tool_call.name == "calculator"
        assert tool_call.arguments == {"expression": "2 + 2"}
        assert tool_call.call_id.startswith("call_")
    
    def test_tool_call_with_custom_id(self):
        """Test tool call with custom ID."""
        tool_call = ToolCall(
            name="weather",
            arguments={"city": "Tokyo"},
            call_id="custom_123"
        )
        
        assert tool_call.call_id == "custom_123"


class TestToolResult:
    """Test ToolResult class functionality."""
    
    def test_successful_tool_result(self):
        """Test successful tool result."""
        result = ToolResult(
            call_id="test_123",
            result=42,
            execution_time=0.1
        )
        
        assert result.call_id == "test_123"
        assert result.result == 42
        assert result.error is None
        assert result.execution_time == 0.1
    
    def test_failed_tool_result(self):
        """Test failed tool result."""
        result = ToolResult(
            call_id="test_456",
            error="Division by zero",
            execution_time=0.05
        )
        
        assert result.call_id == "test_456"
        assert result.result is None
        assert result.error == "Division by zero"
        assert result.execution_time == 0.05


class TestAgentResponse:
    """Test AgentResponse class functionality."""
    
    def test_simple_response(self):
        """Test simple text response."""
        response = AgentResponse(
            content="Hello, how can I help you?"
        )
        
        assert response.content == "Hello, how can I help you?"
        assert response.tool_calls == []
        assert not response.has_tool_calls
        assert response.finish_reason == "completed"
    
    def test_response_with_tool_calls(self):
        """Test response with tool calls."""
        tool_calls = [
            ToolCall(name="calculator", arguments={"x": 1, "y": 2}),
            ToolCall(name="weather", arguments={"city": "NYC"})
        ]
        
        response = AgentResponse(
            content="I'll calculate that for you.",
            tool_calls=tool_calls
        )
        
        assert response.has_tool_calls
        assert len(response.tool_calls) == 2
        assert response.tool_calls[0].name == "calculator"


class TestConfigs:
    """Test configuration classes."""
    
    def test_llm_config_defaults(self):
        """Test LLM configuration defaults."""
        config = LLMConfig(model="gpt-4")
        
        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens is None
        assert config.top_p == 1.0
        assert config.stream is False
    
    def test_llm_config_custom(self):
        """Test LLM configuration with custom values."""
        config = LLMConfig(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=1000,
            stream=True
        )
        
        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.5
        assert config.max_tokens == 1000
        assert config.stream is True
    
    def test_agent_config_defaults(self):
        """Test Agent configuration defaults."""
        config = AgentConfig()
        
        assert config.name == "Agent"
        assert config.system_prompt == "You are a helpful AI assistant."
        assert config.memory_backend == "dict"
        assert config.max_memory_messages == 100
        assert config.tool_timeout == 30.0
        assert config.enable_streaming is False
    
    def test_agent_config_custom(self):
        """Test Agent configuration with custom values."""
        config = AgentConfig(
            name="CustomBot",
            system_prompt="You are a specialized assistant.",
            memory_backend="sqlite",
            max_memory_messages=50
        )
        
        assert config.name == "CustomBot"
        assert config.system_prompt == "You are a specialized assistant."
        assert config.memory_backend == "sqlite"
        assert config.max_memory_messages == 50


if __name__ == "__main__":
    pytest.main([__file__])
