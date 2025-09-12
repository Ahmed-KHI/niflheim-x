"""
Tests for Agent class functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from niflheim_x.core.agent import Agent
from niflheim_x.core.types import Message, MessageRole, AgentResponse
from niflheim_x.core.memory import DictMemory
from niflheim_x.llms.base import LLMAdapter


class MockLLMAdapter(LLMAdapter):
    """Mock LLM adapter for testing."""
    
    def __init__(self, responses=None):
        from niflheim_x.core.types import LLMConfig
        super().__init__(LLMConfig(model="mock"))
        self.responses = responses or ["Mock response"]
        self.call_count = 0
    
    async def generate_response(self, messages, tools=None, stream=False):
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return AgentResponse(content=response)
    
    async def stream_response(self, messages, tools=None):
        from niflheim_x.core.types import StreamingToken
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        
        # Yield tokens one by one
        for char in response:
            yield StreamingToken(content=char)


class TestAgent:
    """Test Agent class functionality."""
    
    @pytest.mark.asyncio
    async def test_agent_creation(self):
        """Test basic agent creation."""
        llm = MockLLMAdapter()
        agent = Agent(
            llm=llm,
            name="TestAgent",
            system_prompt="You are a test agent."
        )
        
        assert agent.name == "TestAgent"
        assert agent.config.system_prompt == "You are a test agent."
        assert isinstance(agent.memory, DictMemory)
        assert agent.session_id is not None
    
    @pytest.mark.asyncio
    async def test_basic_chat(self):
        """Test basic chat functionality."""
        llm = MockLLMAdapter(responses=["Hello! How can I help you?"])
        agent = Agent(llm=llm, name="ChatBot")
        
        response = await agent.chat("Hello")
        
        assert isinstance(response, AgentResponse)
        assert response.content == "Hello! How can I help you?"
        
        # Check that messages were added to memory
        history = await agent.get_conversation_history()
        assert len(history) >= 2  # System message + user message + assistant response
        
        # Find user and assistant messages
        user_msg = next(msg for msg in history if msg.role == MessageRole.USER)
        assistant_msg = next(msg for msg in history if msg.role == MessageRole.ASSISTANT)
        
        assert user_msg.content == "Hello"
        assert assistant_msg.content == "Hello! How can I help you?"
    
    @pytest.mark.asyncio
    async def test_tool_registration(self):
        """Test tool registration and usage."""
        llm = MockLLMAdapter()
        agent = Agent(llm=llm)
        
        @agent.tool(description="Add two numbers")
        def add(x: int, y: int) -> int:
            return x + y
        
        tools = agent.get_available_tools()
        assert len(tools) == 1
        assert tools[0].name == "add"
        assert tools[0].description == "Add two numbers"
    
    @pytest.mark.asyncio
    async def test_memory_persistence(self):
        """Test that conversation memory persists."""
        llm = MockLLMAdapter(responses=["Response 1", "Response 2"])
        agent = Agent(llm=llm)
        
        # First conversation
        await agent.chat("Message 1")
        await agent.chat("Message 2")
        
        # Check history
        history = await agent.get_conversation_history()
        user_messages = [msg for msg in history if msg.role == MessageRole.USER]
        
        assert len(user_messages) == 2
        assert user_messages[0].content == "Message 1"
        assert user_messages[1].content == "Message 2"
    
    @pytest.mark.asyncio
    async def test_clear_memory(self):
        """Test clearing conversation memory."""
        llm = MockLLMAdapter()
        agent = Agent(llm=llm)
        
        # Add some messages
        await agent.chat("Test message")
        
        history_before = await agent.get_conversation_history()
        assert len(history_before) > 1  # At least system + user + assistant
        
        # Clear memory
        await agent.clear_memory()
        
        history_after = await agent.get_conversation_history()
        # Should only have system message after clearing
        assert len(history_after) == 1
        assert history_after[0].role == MessageRole.SYSTEM
    
    @pytest.mark.asyncio
    async def test_custom_memory_backend(self):
        """Test using custom memory backend."""
        llm = MockLLMAdapter()
        custom_memory = DictMemory(max_messages=5)
        
        agent = Agent(
            llm=llm,
            memory_backend=custom_memory
        )
        
        assert agent.memory is custom_memory
    
    @pytest.mark.asyncio
    async def test_streaming_response(self):
        """Test streaming response functionality."""
        llm = MockLLMAdapter(responses=["Hello world!"])
        agent = Agent(llm=llm)
        
        tokens = []
        async for token in agent.chat_stream("Test"):
            tokens.append(token.content)
        
        complete_response = "".join(tokens)
        assert complete_response == "Hello world!"
    
    @pytest.mark.asyncio
    async def test_agent_context_manager(self):
        """Test agent as async context manager."""
        llm = MockLLMAdapter()
        
        async with Agent(llm=llm) as agent:
            response = await agent.chat("Test")
            assert isinstance(response, AgentResponse)


if __name__ == "__main__":
    pytest.main([__file__])
