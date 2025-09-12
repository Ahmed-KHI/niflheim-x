"""
Tests for tool system.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock

from niflheim_x.core.tools import (
    Tool, 
    ToolRegistry, 
    tool,
    _extract_function_schema,
    _python_type_to_json_schema
)
from niflheim_x.core.types import ToolCall, ToolResult


class TestTool:
    """Test Tool class functionality."""
    
    def test_tool_creation(self):
        """Test basic tool creation."""
        def sample_func(x: int, y: str) -> str:
            return f"{x}: {y}"
        
        tool_obj = Tool(
            name="sample",
            description="A sample function",
            function=sample_func,
            parameters={"type": "object", "properties": {}, "required": []},
            timeout=10.0
        )
        
        assert tool_obj.name == "sample"
        assert tool_obj.description == "A sample function"
        assert tool_obj.function == sample_func
        assert tool_obj.timeout == 10.0
    
    def test_to_openai_format(self):
        """Test OpenAI format conversion."""
        def sample_func():
            pass
        
        tool_obj = Tool(
            name="test_tool",
            description="Test description",
            function=sample_func,
            parameters={"type": "object", "properties": {"x": {"type": "integer"}}, "required": ["x"]}
        )
        
        openai_format = tool_obj.to_openai_format()
        
        assert openai_format["type"] == "function"
        assert openai_format["function"]["name"] == "test_tool"
        assert openai_format["function"]["description"] == "Test description"
        assert openai_format["function"]["parameters"]["type"] == "object"
    
    def test_to_anthropic_format(self):
        """Test Anthropic format conversion."""
        def sample_func():
            pass
        
        tool_obj = Tool(
            name="test_tool",
            description="Test description", 
            function=sample_func,
            parameters={"type": "object", "properties": {"x": {"type": "integer"}}, "required": ["x"]}
        )
        
        anthropic_format = tool_obj.to_anthropic_format()
        
        assert anthropic_format["name"] == "test_tool"
        assert anthropic_format["description"] == "Test description"
        assert anthropic_format["input_schema"]["type"] == "object"


class TestToolRegistry:
    """Test ToolRegistry functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = ToolRegistry()
    
    def test_register_and_get_tool(self):
        """Test registering and retrieving tools."""
        def sample_func():
            return "test"
        
        tool_obj = Tool(
            name="sample",
            description="Sample tool",
            function=sample_func,
            parameters={"type": "object", "properties": {}, "required": []}
        )
        
        self.registry.register_tool(tool_obj)
        
        retrieved = self.registry.get_tool("sample")
        assert retrieved is not None
        assert retrieved.name == "sample"
        assert retrieved.function == sample_func
    
    def test_get_nonexistent_tool(self):
        """Test retrieving non-existent tool."""
        result = self.registry.get_tool("nonexistent")
        assert result is None
    
    def test_list_tools(self):
        """Test listing all tools."""
        tools = [
            Tool("tool1", "Description 1", lambda: 1, {}),
            Tool("tool2", "Description 2", lambda: 2, {}),
        ]
        
        for tool in tools:
            self.registry.register_tool(tool)
        
        all_tools = self.registry.list_tools()
        assert len(all_tools) == 2
        assert all_tools[0].name == "tool1"
        assert all_tools[1].name == "tool2"
    
    @pytest.mark.asyncio
    async def test_execute_tool_success(self):
        """Test successful tool execution."""
        def add_numbers(a: int, b: int) -> int:
            return a + b
        
        tool_obj = Tool(
            name="add",
            description="Add two numbers",
            function=add_numbers,
            parameters={}
        )
        
        self.registry.register_tool(tool_obj)
        
        tool_call = ToolCall(
            name="add",
            arguments={"a": 5, "b": 3},
            call_id="test_123"
        )
        
        result = await self.registry.execute_tool(tool_call)
        
        assert result.call_id == "test_123"
        assert result.result == 8
        assert result.error is None
        assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_execute_nonexistent_tool(self):
        """Test executing non-existent tool."""
        tool_call = ToolCall(
            name="nonexistent",
            arguments={},
            call_id="test_456"
        )
        
        result = await self.registry.execute_tool(tool_call)
        
        assert result.call_id == "test_456"
        assert result.result is None
        assert result.error is not None
        assert "not found" in result.error
    
    @pytest.mark.asyncio
    async def test_execute_tool_with_error(self):
        """Test tool execution that raises an error."""
        def failing_function():
            raise ValueError("Something went wrong")
        
        tool_obj = Tool(
            name="failing",
            description="A failing function",
            function=failing_function,
            parameters={}
        )
        
        self.registry.register_tool(tool_obj)
        
        tool_call = ToolCall(
            name="failing",
            arguments={},
            call_id="test_789"
        )
        
        result = await self.registry.execute_tool(tool_call)
        
        assert result.call_id == "test_789"
        assert result.result is None
        assert result.error is not None
        assert "Something went wrong" in result.error
    
    @pytest.mark.asyncio
    async def test_execute_async_tool(self):
        """Test executing async tool function."""
        async def async_function(x: int) -> int:
            await asyncio.sleep(0.01)  # Small delay
            return x * 2
        
        tool_obj = Tool(
            name="async_tool",
            description="An async function",
            function=async_function,
            parameters={}
        )
        
        self.registry.register_tool(tool_obj)
        
        tool_call = ToolCall(
            name="async_tool",
            arguments={"x": 5},
            call_id="async_123"
        )
        
        result = await self.registry.execute_tool(tool_call)
        
        assert result.call_id == "async_123"
        assert result.result == 10
        assert result.error is None


class TestToolDecorator:
    """Test the @tool decorator."""
    
    def test_simple_decorator(self):
        """Test basic tool decoration."""
        @tool(description="Add two numbers")
        def add(a: int, b: int) -> int:
            """Add two numbers together.
            
            a: First number
            b: Second number
            """
            return a + b
        
        # Check that the tool metadata was attached
        assert hasattr(add, '_niflheim_tool')
        tool_obj = add._niflheim_tool
        
        assert tool_obj.name == "add"
        assert tool_obj.description == "Add two numbers"
        # Check that the function is callable (don't compare identity since decorator may wrap it)
        assert callable(tool_obj.function)
        assert tool_obj.function(2, 3) == 5
    
    def test_decorator_with_custom_name(self):
        """Test decorator with custom tool name."""
        @tool(name="calculator", description="Perform calculation")
        def calc(expr: str) -> float:
            return eval(expr)
        
        tool_obj = calc._niflheim_tool
        assert tool_obj.name == "calculator"
    
    def test_decorator_without_args(self):
        """Test decorator used without arguments."""
        @tool()
        def simple_func() -> str:
            """A simple function."""
            return "hello"
        
        tool_obj = simple_func._niflheim_tool
        assert tool_obj.name == "simple_func"
        assert "simple function" in tool_obj.description.lower()
    
    def test_function_still_callable(self):
        """Test that decorated function is still callable."""
        @tool()
        def multiply(x: int, y: int) -> int:
            return x * y
        
        # Function should still work normally
        result = multiply(3, 4)
        assert result == 12


class TestSchemaExtraction:
    """Test function schema extraction utilities."""
    
    def test_extract_basic_schema(self):
        """Test extracting schema from a basic function."""
        def example_func(name: str, age: int, active: bool = True) -> str:
            """Example function.
            
            name: Person's name
            age: Person's age
            active: Whether person is active
            """
            return f"{name} is {age} years old"
        
        schema = _extract_function_schema(example_func)
        
        assert schema["type"] == "object"
        assert "name" in schema["properties"]
        assert "age" in schema["properties"]
        assert "active" in schema["properties"]
        
        # Required parameters (no default value)
        assert "name" in schema["required"]
        assert "age" in schema["required"]
        assert "active" not in schema["required"]  # Has default value
        
        # Check types
        assert schema["properties"]["name"]["type"] == "string"
        assert schema["properties"]["age"]["type"] == "integer"
        assert schema["properties"]["active"]["type"] == "boolean"
    
    def test_python_type_conversion(self):
        """Test Python type to JSON schema conversion."""
        assert _python_type_to_json_schema(str) == {"type": "string"}
        assert _python_type_to_json_schema(int) == {"type": "integer"}
        assert _python_type_to_json_schema(float) == {"type": "number"}
        assert _python_type_to_json_schema(bool) == {"type": "boolean"}
        assert _python_type_to_json_schema(list) == {"type": "array"}
        assert _python_type_to_json_schema(dict) == {"type": "object"}


if __name__ == "__main__":
    pytest.main([__file__])
