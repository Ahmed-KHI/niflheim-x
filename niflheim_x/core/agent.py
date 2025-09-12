"""
Core Agent class for Niflheim_x.

This module contains the main Agent class that orchestrates conversations,
manages memory, executes tools, and interfaces with LLM providers.
"""

import uuid
from typing import Dict, List, Optional, Union, AsyncIterator

from .types import (
    Message, 
    MessageRole, 
    AgentResponse, 
    AgentConfig,
    ToolCall,
    ToolResult,
    StreamingToken
)
from .memory import MemoryBackend, create_memory_backend
from .tools import Tool, ToolRegistry
from ..llms.base import LLMAdapter


class Agent:
    """Main agent class for conversational AI.
    
    The Agent manages conversations with users, maintains memory across sessions,
    executes tools, and generates responses using configured LLM providers.
    
    Attributes:
        name: Name of the agent
        llm: LLM adapter for generating responses  
        memory: Memory backend for storing conversation history
        tools: Registry of available tools
        config: Agent configuration
        session_id: Current conversation session ID
    """
    
    def __init__(
        self,
        llm: LLMAdapter,
        name: str = "Agent",
        system_prompt: str = "You are a helpful AI assistant.",
        memory_backend: Union[str, MemoryBackend] = "dict",
        session_id: Optional[str] = None,
        config: Optional[AgentConfig] = None,
        **memory_kwargs
    ):
        """Initialize the agent.
        
        Args:
            llm: LLM adapter for generating responses
            name: Name of the agent (default: "Agent")
            system_prompt: System prompt for the agent
            memory_backend: Memory backend type or instance
            session_id: Session ID (auto-generated if None)
            config: Agent configuration
            **memory_kwargs: Additional arguments for memory backend
        """
        self.name = name
        self.llm = llm
        self.session_id = session_id or str(uuid.uuid4())
        
        # Set up configuration
        self.config = config or AgentConfig(
            name=name,
            system_prompt=system_prompt,
            memory_backend=memory_backend if isinstance(memory_backend, str) else "custom"
        )
        
        # Set up memory backend
        if isinstance(memory_backend, str):
            self.memory = create_memory_backend(memory_backend, **memory_kwargs)
        else:
            self.memory = memory_backend
        
        # Set up tool registry
        self.tools = ToolRegistry()
        
        # Add system message to memory
        self._add_system_message()
    
    def _add_system_message(self) -> None:
        """Add the system prompt to memory if not already present."""
        import asyncio
        
        # Check if we already have a system message
        try:
            loop = asyncio.get_running_loop()
            task = asyncio.create_task(self.memory.get_messages(self.session_id, limit=1))
            # Don't await here since this might be called from __init__
        except RuntimeError:
            # No event loop running, we'll add it later
            pass
    
    async def _ensure_system_message(self) -> None:
        """Ensure system message is present in memory."""
        messages = await self.memory.get_messages(self.session_id, limit=1)
        
        if not messages or messages[0].role != MessageRole.SYSTEM:
            system_message = Message(
                role=MessageRole.SYSTEM,
                content=self.config.system_prompt,
                agent_name=self.name
            )
            # For now, we'll add to beginning by clearing and re-adding
            # In a real implementation, you'd want a more sophisticated approach
            all_messages = await self.memory.get_messages(self.session_id)
            await self.memory.clear_session(self.session_id)
            await self.memory.add_message(self.session_id, system_message)
            for msg in all_messages:
                if msg.role != MessageRole.SYSTEM:
                    await self.memory.add_message(self.session_id, msg)
    
    def tool(self, func_or_name=None, **kwargs):
        """Decorator to register a function as a tool.
        
        Args:
            func_or_name: Function to register or name of the tool
            **kwargs: Additional tool configuration
            
        Returns:
            Decorated function or decorator
            
        Example:
            @agent.tool
            def calculator(x: int, y: int) -> int:
                return x + y
        """
        from .tools import tool
        
        def decorator(func):
            # Create the tool using the global tool decorator
            decorated_func = tool(**kwargs)(func)
            
            # Register the tool with this agent
            tool_obj = decorated_func._niflheim_tool  # type: ignore
            self.tools.register_tool(tool_obj)
            
            return decorated_func
        
        if callable(func_or_name):
            # Called as @agent.tool (without parentheses)
            return decorator(func_or_name)
        else:
            # Called as @agent.tool(name="...") or @agent.tool()
            if func_or_name is not None:
                kwargs['name'] = func_or_name
            return decorator
    
    def register_tool(self, tool: Tool) -> None:
        """Register a tool with the agent.
        
        Args:
            tool: Tool to register
        """
        self.tools.register_tool(tool)
    
    async def chat(
        self, 
        message: str, 
        stream: bool = False
    ) -> AgentResponse:
        """Chat with the agent.
        
        Args:
            message: User message
            stream: Whether to stream the response (not yet implemented)
            
        Returns:
            Agent response
        """
        # Ensure system message is present
        await self._ensure_system_message()
        
        # Add user message to memory
        user_message = Message(
            role=MessageRole.USER,
            content=message
        )
        await self.memory.add_message(self.session_id, user_message)
        
        # Get conversation history
        messages = await self.memory.get_messages(
            self.session_id, 
            limit=self.config.max_memory_messages
        )
        
        # Get available tools for the LLM
        llm_tools = None
        if self.tools.list_tools():
            # Convert tools to the format expected by the LLM
            if hasattr(self.llm, 'get_openai_tools'):
                llm_tools = self.tools.get_openai_tools()
            else:
                llm_tools = self.tools.get_anthropic_tools()
        
        # Always return AgentResponse for now (streaming to be implemented later)
        return await self._generate_response(messages, llm_tools)
    
    async def chat_stream(
        self, 
        message: str
    ) -> AsyncIterator[StreamingToken]:
        """Chat with the agent using streaming responses.
        
        Args:
            message: User message
            
        Yields:
            Streaming tokens
        """
        # Ensure system message is present
        await self._ensure_system_message()
        
        # Add user message to memory
        user_message = Message(
            role=MessageRole.USER,
            content=message
        )
        await self.memory.add_message(self.session_id, user_message)
        
        # Get conversation history
        messages = await self.memory.get_messages(
            self.session_id, 
            limit=self.config.max_memory_messages
        )
        
        # Get available tools for the LLM
        llm_tools = None
        if self.tools.list_tools():
            # Convert tools to the format expected by the LLM
            if hasattr(self.llm, 'get_openai_tools'):
                llm_tools = self.tools.get_openai_tools()
            else:
                llm_tools = self.tools.get_anthropic_tools()
        
        async for token in self._stream_response(messages, llm_tools):
            yield token
    
    async def _generate_response(
        self, 
        messages: List[Message], 
        tools: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Generate a non-streaming response.
        
        Args:
            messages: Conversation messages
            tools: Available tools
            
        Returns:
            Generated response
        """
        # Generate response from LLM
        response = await self.llm.generate_response(messages, tools)
        
        # Execute any tool calls
        if response.has_tool_calls:
            tool_results = []
            for tool_call in response.tool_calls:
                result = await self.tools.execute_tool(tool_call)
                tool_results.append(result)
            
            # Add tool call and results to memory
            assistant_message = Message(
                role=MessageRole.ASSISTANT,
                content=response.content,
                agent_name=self.name,
                metadata={"tool_calls": [tc.call_id for tc in response.tool_calls]}
            )
            await self.memory.add_message(self.session_id, assistant_message)
            
            # Add tool results as messages
            for result in tool_results:
                tool_message = Message(
                    role=MessageRole.TOOL,
                    content=str(result.result) if result.result is not None else result.error or "",
                    metadata={"call_id": result.call_id, "execution_time": result.execution_time}
                )
                await self.memory.add_message(self.session_id, tool_message)
            
            # Get updated messages and generate final response
            updated_messages = await self.memory.get_messages(
                self.session_id, 
                limit=self.config.max_memory_messages
            )
            
            final_response = await self.llm.generate_response(updated_messages)
            
            # Add final response to memory
            final_message = Message(
                role=MessageRole.ASSISTANT,
                content=final_response.content,
                agent_name=self.name
            )
            await self.memory.add_message(self.session_id, final_message)
            
            return final_response
        
        else:
            # No tool calls, just add response to memory
            assistant_message = Message(
                role=MessageRole.ASSISTANT,
                content=response.content,
                agent_name=self.name
            )
            await self.memory.add_message(self.session_id, assistant_message)
            
            return response
    
    async def _stream_response(
        self, 
        messages: List[Message], 
        tools: Optional[List[Dict]] = None
    ) -> AsyncIterator[StreamingToken]:
        """Generate a streaming response.
        
        Args:
            messages: Conversation messages
            tools: Available tools
            
        Yields:
            Streaming tokens
        """
        from typing import cast
        content_parts = []
        
        # Create the async generator with proper typing
        stream_generator = cast(AsyncIterator[StreamingToken], self.llm.stream_response(messages, tools))
        async for token in stream_generator:
            content_parts.append(token.content)
            yield token
        
        # Add the complete response to memory
        complete_content = "".join(content_parts)
        assistant_message = Message(
            role=MessageRole.ASSISTANT,
            content=complete_content,
            agent_name=self.name
        )
        await self.memory.add_message(self.session_id, assistant_message)
    
    async def clear_memory(self) -> None:
        """Clear the agent's conversation memory."""
        await self.memory.clear_session(self.session_id)
        await self._ensure_system_message()
    
    async def get_conversation_history(self, limit: Optional[int] = None) -> List[Message]:
        """Get the conversation history.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of messages in chronological order
        """
        return await self.memory.get_messages(self.session_id, limit)
    
    def get_available_tools(self) -> List[Tool]:
        """Get list of available tools.
        
        Returns:
            List of registered tools
        """
        return self.tools.list_tools()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if hasattr(self.llm, '__aexit__'):
            await self.llm.__aexit__(exc_type, exc_val, exc_tb)  # type: ignore
