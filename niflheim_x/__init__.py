"""
Niflheim_x - A lightweight, composable Agent Orchestration Framework

The fast alternative to LangChain for building AI agents.
"""

__version__ = "0.1.0"
__author__ = "Ahmed KHI"
__email__ = "ahmed@khitech.dev"

# Core imports for easy access
from .core.agent import Agent
from .core.memory import MemoryBackend, DictMemory, SQLiteMemory
from .core.tools import Tool, tool
from .core.orchestrator import AgentOrchestrator
from .core.types import Message, AgentResponse, ToolCall
from .llms.openai import OpenAIAdapter
from .llms.anthropic import AnthropicAdapter
from .llms.base import LLMAdapter

__all__ = [
    # Core classes
    "Agent",
    "AgentOrchestrator",
    
    # Memory backends
    "MemoryBackend", 
    "DictMemory",
    "SQLiteMemory",
    
    # Tools
    "Tool",
    "tool",
    
    # Types
    "Message",
    "AgentResponse", 
    "ToolCall",
    
    # LLM Adapters
    "LLMAdapter",
    "OpenAIAdapter",
    "AnthropicAdapter",
]
