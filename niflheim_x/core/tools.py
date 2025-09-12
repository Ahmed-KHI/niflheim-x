"""
Tool system for registering and executing functions as agent tools.

This module provides decorators and classes for registering Python functions
as tools that agents can call during conversations.
"""

import asyncio
import inspect
import json
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, get_type_hints
from dataclasses import dataclass

from .types import ToolCall, ToolResult


@dataclass
class Tool:
    """Represents a callable tool function.
    
    Attributes:
        name: Name of the tool
        description: Description of what the tool does
        function: The actual callable function
        parameters: JSON schema describing the function parameters
        timeout: Maximum execution time in seconds
    """
    name: str
    description: str
    function: Callable[..., Any]
    parameters: Dict[str, Any]
    timeout: float = 30.0
    
    def to_openai_format(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }
    
    def to_anthropic_format(self) -> Dict[str, Any]:
        """Convert tool to Anthropic tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }


class ToolRegistry:
    """Registry for managing agent tools.
    
    This class maintains a collection of available tools and provides
    methods for registering, retrieving, and executing them.
    """
    
    def __init__(self):
        """Initialize an empty tool registry."""
        self._tools: Dict[str, Tool] = {}
    
    def register_tool(self, tool: Tool) -> None:
        """Register a tool in the registry.
        
        Args:
            tool: The tool to register
        """
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name.
        
        Args:
            name: Name of the tool to retrieve
            
        Returns:
            The tool if found, None otherwise
        """
        return self._tools.get(name)
    
    def list_tools(self) -> List[Tool]:
        """Get all registered tools.
        
        Returns:
            List of all registered tools
        """
        return list(self._tools.values())
    
    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Get all tools in OpenAI function calling format.
        
        Returns:
            List of tools formatted for OpenAI API
        """
        return [tool.to_openai_format() for tool in self._tools.values()]
    
    def get_anthropic_tools(self) -> List[Dict[str, Any]]:
        """Get all tools in Anthropic tool format.
        
        Returns:
            List of tools formatted for Anthropic API
        """
        return [tool.to_anthropic_format() for tool in self._tools.values()]
    
    async def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call and return the result.
        
        Args:
            tool_call: The tool call to execute
            
        Returns:
            Result of the tool execution
        """
        import time
        start_time = time.time()
        
        tool = self.get_tool(tool_call.name)
        if not tool:
            return ToolResult(
                call_id=tool_call.call_id,
                error=f"Tool '{tool_call.name}' not found",
                execution_time=time.time() - start_time,
            )
        
        try:
            # Execute the tool function with timeout
            if asyncio.iscoroutinefunction(tool.function):
                result = await asyncio.wait_for(
                    tool.function(**tool_call.arguments),
                    timeout=tool.timeout
                )
            else:
                # Run sync function in thread pool to avoid blocking
                result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: tool.function(**tool_call.arguments)
                )
            
            return ToolResult(
                call_id=tool_call.call_id,
                result=result,
                execution_time=time.time() - start_time,
            )
            
        except asyncio.TimeoutError:
            return ToolResult(
                call_id=tool_call.call_id,
                error=f"Tool execution timed out after {tool.timeout} seconds",
                execution_time=time.time() - start_time,
            )
        except Exception as e:
            return ToolResult(
                call_id=tool_call.call_id,
                error=f"Tool execution failed: {str(e)}",
                execution_time=time.time() - start_time,
            )


def _extract_function_schema(func: Callable[..., Any]) -> Dict[str, Any]:
    """Extract JSON schema from a function's type hints and docstring.
    
    Args:
        func: Function to extract schema from
        
    Returns:
        JSON schema describing the function parameters
    """
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)
    
    properties = {}
    required = []
    
    for param_name, param in signature.parameters.items():
        # Skip self parameter
        if param_name == "self":
            continue
            
        param_type = type_hints.get(param_name, str)
        param_schema = _python_type_to_json_schema(param_type)
        
        # Extract parameter description from docstring
        description = _extract_param_description(func, param_name)
        if description:
            param_schema["description"] = description
        
        properties[param_name] = param_schema
        
        # Check if parameter is required (no default value)
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
    
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def _python_type_to_json_schema(python_type: Any) -> Dict[str, Any]:
    """Convert Python type to JSON schema type.
    
    Args:
        python_type: Python type to convert
        
    Returns:
        JSON schema type definition
    """
    type_mapping = {
        str: {"type": "string"},
        int: {"type": "integer"},
        float: {"type": "number"},
        bool: {"type": "boolean"},
        list: {"type": "array"},
        dict: {"type": "object"},
    }
    
    # Handle Optional types
    if hasattr(python_type, "__origin__"):
        if python_type.__origin__ is list:
            item_type = python_type.__args__[0] if python_type.__args__ else str
            return {
                "type": "array",
                "items": _python_type_to_json_schema(item_type)
            }
        elif python_type.__origin__ is dict:
            return {"type": "object"}
    
    return type_mapping.get(python_type, {"type": "string"})


def _extract_param_description(func: Callable[..., Any], param_name: str) -> Optional[str]:
    """Extract parameter description from function docstring.
    
    Args:
        func: Function to extract from
        param_name: Name of the parameter
        
    Returns:
        Parameter description if found, None otherwise
    """
    if not func.__doc__:
        return None
    
    # Simple docstring parsing - look for "param_name: description" patterns
    lines = func.__doc__.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith(f"{param_name}:"):
            return line[len(f"{param_name}:"):].strip()
    
    return None


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    timeout: float = 30.0
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to register a function as an agent tool.
    
    Args:
        name: Name of the tool (defaults to function name)
        description: Description of what the tool does (defaults to docstring)
        timeout: Maximum execution time in seconds (default: 30.0)
        
    Returns:
        Decorated function
        
    Example:
        @tool(description="Add two numbers together")
        def calculator(a: int, b: int) -> int:
            '''Add two numbers.
            
            a: First number
            b: Second number
            '''
            return a + b
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Extract tool metadata
        tool_name = name or func.__name__
        tool_description = description or (func.__doc__ or "").split("\n")[0].strip()
        
        # Generate parameter schema
        parameters = _extract_function_schema(func)
        
        # Create the tool
        tool_obj = Tool(
            name=tool_name,
            description=tool_description,
            function=func,
            parameters=parameters,
            timeout=timeout,
        )
        
        # Store tool metadata on the function for later registration
        func._niflheim_tool = tool_obj  # type: ignore
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


# Example tools for demonstration
@tool(description="Perform basic mathematical calculations")
def calculator(expression: str) -> float:
    """Evaluate a mathematical expression safely.
    
    expression: Mathematical expression to evaluate (e.g., "2 + 3 * 4")
    """
    # Simple safe evaluation - only allow basic math operations
    allowed_chars = set("0123456789+-*/()., ")
    if not all(c in allowed_chars for c in expression):
        raise ValueError("Expression contains invalid characters")
    
    try:
        # Use eval with restricted environment for safety
        return float(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")


@tool(description="Get current date and time")
def get_current_time() -> str:
    """Get the current date and time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool(description="Generate a random number within a range")
def random_number(min_val: int = 1, max_val: int = 100) -> int:
    """Generate a random integer within the specified range.
    
    min_val: Minimum value (inclusive)
    max_val: Maximum value (inclusive)
    """
    import random
    return random.randint(min_val, max_val)
