"""
Tests for LLM adapters.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from niflheim_x.llms.base import LLMAdapter
from niflheim_x.llms.openai import OpenAIAdapter
from niflheim_x.llms.anthropic import AnthropicAdapter
from niflheim_x.core.types import Message, MessageRole, LLMConfig


class MockLLMAdapter(LLMAdapter):
    """Mock LLM adapter for testing."""
    
    async def generate_response(self, messages, tools=None, stream=False):
        from niflheim_x.core.types import AgentResponse
        return AgentResponse(content="Mock response")
    
    async def stream_response(self, messages, tools=None):
        from niflheim_x.core.types import StreamingToken
        yield StreamingToken(content="Mock")
        yield StreamingToken(content=" token")


class TestLLMAdapter:
    """Test base LLM adapter functionality."""
    
    def test_adapter_initialization(self):
        """Test LLM adapter initialization."""
        config = LLMConfig(model="test-model", temperature=0.5)
        adapter = MockLLMAdapter(config)
        
        assert adapter.config.model == "test-model"
        assert adapter.config.temperature == 0.5
    
    @pytest.mark.asyncio
    async def test_validate_connection(self):
        """Test connection validation."""
        config = LLMConfig(model="test-model")
        adapter = MockLLMAdapter(config)
        
        is_valid = await adapter.validate_connection()
        assert is_valid is True
    
    def test_get_model_info(self):
        """Test getting model information."""
        config = LLMConfig(model="test-model")
        adapter = MockLLMAdapter(config)
        
        info = adapter.get_model_info()
        assert info["model"] == "test-model"
        assert info["provider"] == "mockllm"


class TestOpenAIAdapter:
    """Test OpenAI adapter functionality."""
    
    def test_openai_adapter_creation(self):
        """Test OpenAI adapter creation."""
        adapter = OpenAIAdapter(
            api_key="test-key",
            model="gpt-4",
            temperature=0.7
        )
        
        assert adapter.api_key == "test-key"
        assert adapter.config.model == "gpt-4"
        assert adapter.config.temperature == 0.7
        assert adapter.base_url == "https://api.openai.com/v1"
    
    def test_messages_to_openai_format(self):
        """Test message format conversion."""
        adapter = OpenAIAdapter(api_key="test")
        
        messages = [
            Message(role=MessageRole.SYSTEM, content="System prompt"),
            Message(role=MessageRole.USER, content="User message"),
            Message(role=MessageRole.ASSISTANT, content="Assistant response", agent_name="Bot")
        ]
        
        openai_messages = adapter._messages_to_openai_format(messages)
        
        assert len(openai_messages) == 3
        assert openai_messages[0]["role"] == "system"
        assert openai_messages[0]["content"] == "System prompt"
        assert openai_messages[2]["name"] == "Bot"
    
    @pytest.mark.asyncio
    async def test_openai_generate_response(self):
        """Test OpenAI response generation."""
        # Mock HTTP response
        mock_response = {
            "choices": [{
                "message": {
                    "content": "Test response",
                    "role": "assistant"
                },
                "finish_reason": "stop"
            }],
            "usage": {"total_tokens": 10}
        }
        
        # Create a proper async mock
        async def mock_post(*args, **kwargs):
            mock_resp = AsyncMock()
            mock_resp.json = AsyncMock(return_value=mock_response)
            mock_resp.raise_for_status = MagicMock()  # This doesn't need to be async
            return mock_resp
        
        with patch.object(httpx.AsyncClient, 'post', side_effect=mock_post):
            adapter = OpenAIAdapter(api_key="test")
            messages = [Message(role=MessageRole.USER, content="Hello")]
            
            response = await adapter.generate_response(messages)
            
            assert response.content == "Test response"
            assert response.usage["total_tokens"] == 10


class TestAnthropicAdapter:
    """Test Anthropic adapter functionality."""
    
    def test_anthropic_adapter_creation(self):
        """Test Anthropic adapter creation."""
        adapter = AnthropicAdapter(
            api_key="test-key",
            model="claude-3-5-sonnet-20241022",
            temperature=0.5
        )
        
        assert adapter.api_key == "test-key"
        assert adapter.config.model == "claude-3-5-sonnet-20241022"
        assert adapter.config.temperature == 0.5
        assert adapter.base_url == "https://api.anthropic.com"
    
    def test_messages_to_anthropic_format(self):
        """Test message format conversion for Anthropic."""
        adapter = AnthropicAdapter(api_key="test")
        
        messages = [
            Message(role=MessageRole.SYSTEM, content="System prompt"),
            Message(role=MessageRole.USER, content="User message"),
            Message(role=MessageRole.ASSISTANT, content="Assistant response")
        ]
        
        system_prompt, conversation = adapter._messages_to_anthropic_format(messages)
        
        assert system_prompt == "System prompt"
        assert len(conversation) == 2
        assert conversation[0]["role"] == "user"
        assert conversation[1]["role"] == "assistant"
    
    @pytest.mark.asyncio
    async def test_anthropic_generate_response(self):
        """Test Anthropic response generation."""
        # Mock HTTP response
        mock_response = {
            "content": [
                {"type": "text", "text": "Test response from Claude"}
            ],
            "usage": {"input_tokens": 5, "output_tokens": 8},
            "stop_reason": "end_turn"
        }
        
        # Create a proper async mock
        async def mock_post(*args, **kwargs):
            mock_resp = AsyncMock()
            mock_resp.json = AsyncMock(return_value=mock_response)
            mock_resp.raise_for_status = MagicMock()  # This doesn't need to be async
            return mock_resp
        
        with patch.object(httpx.AsyncClient, 'post', side_effect=mock_post):
            adapter = AnthropicAdapter(api_key="test")
            messages = [Message(role=MessageRole.USER, content="Hello")]
            
            response = await adapter.generate_response(messages)
            
            assert response.content == "Test response from Claude"
            assert response.finish_reason == "end_turn"


if __name__ == "__main__":
    pytest.main([__file__])
