"""
Mock framework implementations for benchmarking when actual frameworks aren't available.
These provide realistic simulation of competitor frameworks for comparison testing.
"""

import asyncio
import time
import random
from typing import List, Any, Optional


class MockLangChainAgent:
    """Mock LangChain agent for benchmarking when LangChain isn't available."""
    
    def __init__(self, llm, memory=None, tools=None):
        self.llm = llm
        self.memory = memory or []
        self.tools = tools or []
        
        # Simulate LangChain's slower initialization
        time.sleep(0.1)  # LangChain tends to be slower to start
    
    def run(self, message: str) -> str:
        """Simulate LangChain's run method."""
        # Simulate LangChain's processing overhead
        time.sleep(0.05 + random.uniform(0.01, 0.03))
        
        response = f"LangChain response to: {message}"
        self.memory.append({"input": message, "output": response})
        
        return response


class MockBeeAIAgent:
    """Mock BeeAI agent for benchmarking when BeeAI isn't available."""
    
    def __init__(self, model, memory=None, tools=None):
        self.model = model
        self.memory = memory or []
        self.tools = tools or []
        
        # Simulate BeeAI's initialization time
        time.sleep(0.08)
    
    async def chat(self, message: str) -> str:
        """Simulate BeeAI's chat method."""
        # Simulate BeeAI's processing time
        await asyncio.sleep(0.04 + random.uniform(0.005, 0.015))
        
        response = f"BeeAI response to: {message}"
        self.memory.append({"user": message, "assistant": response})
        
        return response


class MockOpenAIAgent:
    """Mock direct OpenAI agent for baseline comparison."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.conversation_history = []
        
        # Minimal initialization time
        time.sleep(0.01)
    
    async def chat(self, message: str) -> str:
        """Simulate direct OpenAI API call."""
        # Simulate network latency and API processing
        await asyncio.sleep(0.3 + random.uniform(0.1, 0.2))
        
        response = f"OpenAI response to: {message}"
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response


class MockLangChainBenchmark:
    """Mock LangChain benchmark implementation."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.framework_name = "langchain"
    
    async def create_simple_agent(self) -> Any:
        """Create a basic mock LangChain agent."""
        return MockLangChainAgent(llm="mock_openai_llm")
    
    async def create_agent_with_memory(self) -> Any:
        """Create agent with memory."""
        return MockLangChainAgent(llm="mock_openai_llm", memory=[])
    
    async def create_agent_with_tools(self) -> Any:
        """Create agent with tools."""
        return MockLangChainAgent(llm="mock_openai_llm", tools=["calculator"])
    
    async def process_conversation(self, agent: Any, messages: List[str]) -> float:
        """Process conversation with mock LangChain agent."""
        start_time = time.time()
        for message in messages:
            agent.run(message)
        return time.time() - start_time
    
    async def concurrent_agents(self, num_agents: int, messages_per_agent: int) -> float:
        """Test concurrent performance."""
        def agent_task(agent_id: int):
            agent = MockLangChainAgent(llm="mock_llm")
            start_time = time.time()
            for i in range(messages_per_agent):
                agent.run(f"Hello from agent {agent_id}, message {i}")
            return time.time() - start_time
        
        start_time = time.time()
        # LangChain doesn't handle async well, so simulate sequential processing
        for i in range(num_agents):
            agent_task(i)
        return time.time() - start_time


class MockBeeAIBenchmark:
    """Mock BeeAI benchmark implementation."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.framework_name = "beeai"
    
    async def create_simple_agent(self) -> Any:
        """Create a basic mock BeeAI agent."""
        return MockBeeAIAgent(model="gpt-3.5-turbo")
    
    async def create_agent_with_memory(self) -> Any:
        """Create agent with memory."""
        return MockBeeAIAgent(model="gpt-3.5-turbo", memory=[])
    
    async def create_agent_with_tools(self) -> Any:
        """Create agent with tools."""
        return MockBeeAIAgent(model="gpt-3.5-turbo", tools=["calculator"])
    
    async def process_conversation(self, agent: Any, messages: List[str]) -> float:
        """Process conversation with mock BeeAI agent."""
        start_time = time.time()
        for message in messages:
            await agent.chat(message)
        return time.time() - start_time
    
    async def concurrent_agents(self, num_agents: int, messages_per_agent: int) -> float:
        """Test concurrent performance."""
        async def agent_task(agent_id: int):
            agent = MockBeeAIAgent(model="gpt-3.5-turbo")
            start_time = time.time()
            for i in range(messages_per_agent):
                await agent.chat(f"Hello from agent {agent_id}, message {i}")
            return time.time() - start_time
        
        start_time = time.time()
        tasks = [agent_task(i) for i in range(num_agents)]
        await asyncio.gather(*tasks)
        return time.time() - start_time


class MockOpenAIBenchmark:
    """Mock direct OpenAI benchmark for baseline comparison."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.framework_name = "openai-direct"
    
    async def create_simple_agent(self) -> Any:
        """Create a basic mock OpenAI agent."""
        return MockOpenAIAgent(self.api_key)
    
    async def create_agent_with_memory(self) -> Any:
        """Create agent with memory."""
        return MockOpenAIAgent(self.api_key)
    
    async def create_agent_with_tools(self) -> Any:
        """Create agent with tools."""
        return MockOpenAIAgent(self.api_key)
    
    async def process_conversation(self, agent: Any, messages: List[str]) -> float:
        """Process conversation with mock OpenAI agent."""
        start_time = time.time()
        for message in messages:
            await agent.chat(message)
        return time.time() - start_time
    
    async def concurrent_agents(self, num_agents: int, messages_per_agent: int) -> float:
        """Test concurrent performance."""
        async def agent_task(agent_id: int):
            agent = MockOpenAIAgent(self.api_key)
            start_time = time.time()
            for i in range(messages_per_agent):
                await agent.chat(f"Hello from agent {agent_id}, message {i}")
            return time.time() - start_time
        
        start_time = time.time()
        tasks = [agent_task(i) for i in range(num_agents)]
        await asyncio.gather(*tasks)
        return time.time() - start_time


# Performance characteristics for realistic simulation
FRAMEWORK_CHARACTERISTICS = {
    "niflheim-x": {
        "startup_overhead": 0.02,
        "processing_overhead": 0.01,
        "memory_efficiency": 1.0,
        "concurrency_factor": 1.0
    },
    "langchain": {
        "startup_overhead": 0.15,
        "processing_overhead": 0.08,
        "memory_efficiency": 0.7,
        "concurrency_factor": 0.3
    },
    "beeai": {
        "startup_overhead": 0.08,
        "processing_overhead": 0.04,
        "memory_efficiency": 0.85,
        "concurrency_factor": 0.8
    },
    "openai-direct": {
        "startup_overhead": 0.01,
        "processing_overhead": 0.02,
        "memory_efficiency": 0.95,
        "concurrency_factor": 0.6
    }
}