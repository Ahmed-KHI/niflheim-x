---
sidebar_position: 1
---

# Quick Start Guide

Get up and running with Niflheim-X in under 5 minutes. This guide will walk you through installation, basic setup, and your first AI agent.

## 🚀 Installation

### Using pip (Recommended)

```bash
pip install niflheim-x
```

### Using Poetry

```bash
poetry add niflheim-x
```

### From Source

```bash
git clone https://github.com/your-org/niflheim-x.git
cd niflheim-x
pip install -e .
```

## 🔧 Basic Setup

### 1. Get API Keys

You'll need an API key from one of the supported providers:

- **OpenAI**: Get your key from [platform.openai.com](https://platform.openai.com/api-keys)
- **Anthropic**: Get your key from [console.anthropic.com](https://console.anthropic.com/)

### 2. Environment Configuration

Create a `.env` file in your project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Anthropic Configuration  
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Optional: Organization ID for OpenAI
OPENAI_ORG_ID=org-your-organization-id
```

### 3. First Agent

Create your first agent in just a few lines:

```python
import asyncio
import os
from niflheim_x import Agent, OpenAILLM

async def main():
    # Create an LLM instance
    llm = OpenAILLM(
        model="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create an agent
    agent = Agent(
        name="MyFirstBot",
        llm=llm,
        system_prompt="You are a helpful assistant that provides clear, concise answers."
    )
    
    # Chat with your agent
    response = await agent.chat("Hello! What can you help me with?")
    print(f"Agent: {response.content}")
    
    # Have a conversation
    response = await agent.chat("Explain quantum computing in simple terms")
    print(f"Agent: {response.content}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run your first agent:

```bash
python my_first_agent.py
```

## 💬 Interactive Chat Example

Create an interactive chat session:

```python
import asyncio
import os
from niflheim_x import Agent, OpenAILLM

async def interactive_chat():
    # Setup
    llm = OpenAILLM(model="gpt-4", api_key=os.getenv("OPENAI_API_KEY"))
    agent = Agent(
        name="ChatBot",
        llm=llm,
        system_prompt="You are a friendly and knowledgeable assistant."
    )
    
    print("🤖 Niflheim-X ChatBot")
    print("Type 'quit' to exit, 'clear' to reset conversation\n")
    
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        # Handle special commands
        if user_input.lower() == 'quit':
            print("Goodbye! 👋")
            break
        elif user_input.lower() == 'clear':
            await agent.clear_conversation()
            print("🔄 Conversation cleared!")
            continue
        elif not user_input:
            continue
        
        try:
            # Get agent response
            print("🤖 Thinking...")
            response = await agent.chat(user_input)
            print(f"Bot: {response.content}\n")
            
        except Exception as e:
            print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(interactive_chat())
```

## 🛠️ Adding Tools

Extend your agent with tools for more capabilities:

```python
import asyncio
import os
import requests
from niflheim_x import Agent, OpenAILLM, Tool

# Define a simple tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    # This is a simplified example - use a real weather API
    weather_data = {
        "New York": "Sunny, 22°C",
        "London": "Cloudy, 15°C", 
        "Tokyo": "Rainy, 18°C"
    }
    
    return weather_data.get(city, f"Weather data not available for {city}")

def calculate_tip(bill_amount: float, tip_percentage: float = 15.0) -> str:
    """Calculate tip and total for a restaurant bill."""
    tip = bill_amount * (tip_percentage / 100)
    total = bill_amount + tip
    return f"Bill: ${bill_amount:.2f}, Tip ({tip_percentage}%): ${tip:.2f}, Total: ${total:.2f}"

async def tool_example():
    # Create LLM
    llm = OpenAILLM(model="gpt-4", api_key=os.getenv("OPENAI_API_KEY"))
    
    # Create tools
    weather_tool = Tool.from_function(
        function=get_weather,
        name="get_weather",
        description="Get current weather information for any city"
    )
    
    tip_tool = Tool.from_function(
        function=calculate_tip,
        name="calculate_tip", 
        description="Calculate tip and total amount for a restaurant bill"
    )
    
    # Create agent with tools
    agent = Agent(
        name="ToolBot",
        llm=llm,
        system_prompt="You are a helpful assistant with access to weather and tip calculation tools."
    )
    
    # Register tools
    agent.register_tool(weather_tool)
    agent.register_tool(tip_tool)
    
    # Test the tools
    print("Testing weather tool:")
    response = await agent.chat("What's the weather like in London?")
    print(f"Agent: {response.content}\n")
    
    print("Testing tip calculator:")
    response = await agent.chat("Calculate a 20% tip for a $85.50 bill")
    print(f"Agent: {response.content}\n")

if __name__ == "__main__":
    asyncio.run(tool_example())
```

## 💾 Adding Memory

Make your agent remember conversations:

```python
import asyncio
import os
from niflheim_x import Agent, OpenAILLM, SQLiteMemory

async def memory_example():
    # Create memory backend
    memory = SQLiteMemory(
        db_path="./chatbot_memory.db",
        session_id="user_123"
    )
    
    # Create agent with memory
    llm = OpenAILLM(model="gpt-4", api_key=os.getenv("OPENAI_API_KEY"))
    agent = Agent(
        name="MemoryBot",
        llm=llm,
        memory=memory,
        system_prompt="You are a helpful assistant with memory. Remember our conversations."
    )
    
    # First conversation
    print("First session:")
    response = await agent.chat("My name is Alice and I love Python programming")
    print(f"Agent: {response.content}")
    
    response = await agent.chat("What's my favorite programming language?") 
    print(f"Agent: {response.content}")
    
    print("\n" + "="*50 + "\n")
    
    # Simulate new session (memory persists)
    print("New session (memory persists):")
    response = await agent.chat("Do you remember my name?")
    print(f"Agent: {response.content}")

if __name__ == "__main__":
    asyncio.run(memory_example())
```

## 🌊 Streaming Responses

Get real-time streaming responses:

```python
import asyncio
import os
from niflheim_x import Agent, OpenAILLM

async def streaming_example():
    llm = OpenAILLM(model="gpt-4", api_key=os.getenv("OPENAI_API_KEY"))
    agent = Agent(
        name="StreamBot",
        llm=llm,
        enable_streaming=True
    )
    
    print("🤖 Streaming response example:")
    print("User: Explain how machine learning works\n")
    print("Bot: ", end="", flush=True)
    
    # Stream the response
    async for chunk in agent.stream("Explain how machine learning works in detail"):
        if chunk.content:
            print(chunk.content, end="", flush=True)
        
        if chunk.finished:
            print("\n\n✅ Response complete!")
            break

if __name__ == "__main__":
    asyncio.run(streaming_example())
```

## 🔄 Complete Example: Smart Assistant

Here's a complete example combining all features:

```python
import asyncio
import os
import requests
from datetime import datetime
from niflheim_x import Agent, OpenAILLM, SQLiteMemory, Tool

# Define useful tools
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def search_web(query: str) -> str:
    """Search the web for information (simplified example)."""
    # In a real implementation, use a search API
    return f"Here are search results for '{query}': [This would contain real search results]"

def calculate_math(expression: str) -> str:
    """Safely calculate mathematical expressions."""
    try:
        # Simple math evaluation (extend for more complex math)
        result = eval(expression, {"__builtins__": {}}, {
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow, "len": len
        })
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"

async def smart_assistant():
    # Setup memory
    memory = SQLiteMemory(
        db_path="./assistant_memory.db",
        session_id="main_user"
    )
    
    # Setup LLM
    llm = OpenAILLM(
        model="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7
    )
    
    # Create agent
    agent = Agent(
        name="SmartAssistant",
        llm=llm,
        memory=memory,
        system_prompt="""You are a helpful and intelligent assistant with access to various tools.
        
        You can:
        - Answer questions and have conversations
        - Get the current time and date
        - Search the web for information
        - Perform mathematical calculations
        - Remember our conversation history
        
        Always be helpful, accurate, and use tools when appropriate.""",
        enable_streaming=True
    )
    
    # Register tools
    tools = [
        Tool.from_function(get_current_time, name="get_time"),
        Tool.from_function(search_web, name="search_web"),
        Tool.from_function(calculate_math, name="calculate")
    ]
    
    for tool in tools:
        agent.register_tool(tool)
    
    # Interactive chat
    print("🧠 Smart Assistant with Tools & Memory")
    print("Available commands: 'quit', 'clear', 'help'")
    print("Try asking about time, math problems, or general questions!\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye! 🙋‍♂️")
            break
        elif user_input.lower() == 'clear':
            await agent.clear_conversation()
            print("🔄 Memory cleared!\n")
            continue
        elif user_input.lower() == 'help':
            print("""
Available features:
- Ask for current time: "What time is it?"
- Math calculations: "Calculate 15 * 23 + 47"
- Web search: "Search for Python tutorials"
- General conversation: "Tell me about quantum computing"
- Memory: I remember our entire conversation!
            """)
            continue
        elif not user_input:
            continue
        
        try:
            print("🤖 ", end="", flush=True)
            
            # Stream response
            full_response = ""
            async for chunk in agent.stream(user_input):
                if chunk.content:
                    print(chunk.content, end="", flush=True)
                    full_response += chunk.content
                
                if chunk.finished:
                    print("\n")
                    break
            
        except Exception as e:
            print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(smart_assistant())
```

## 🎯 Next Steps

Now that you have a working agent, explore these advanced features:

### 🏗️ **Core Concepts**
- [Agents](../core/agents) - Deep dive into agent capabilities
- [Memory Systems](../core/memory) - Persistent conversation storage
- [Tools](../core/tools) - Extend agent functionality
- [LLM Providers](../core/llms) - Work with different AI models

### 🏢 **Enterprise Features**  
- [Observability](../enterprise/observability) - Monitor and debug agents
- [Security & Compliance](../enterprise/security) - Enterprise-grade security
- [Multi-Agent Orchestration](../enterprise/orchestration) - Complex workflows

### 📚 **Examples & Guides**
- [Example Applications](../examples/simple-qa-bot) - Ready-to-use examples
- [Performance Optimization](./performance) - Scale your agents
- [Deployment Guide](./deployment) - Production deployment

### 🔧 **Development**
- [API Reference](../api/agent) - Complete API documentation
- [Contributing Guide](../contributing) - Help improve Niflheim-X
- [Troubleshooting](./troubleshooting) - Common issues and solutions

## 📞 Getting Help

- **Documentation**: You're reading it! 📖
- **GitHub Issues**: [Report bugs or request features](https://github.com/your-org/niflheim-x/issues)
- **Community Discord**: [Join our developer community](https://discord.gg/niflheim-x)
- **Email Support**: [enterprise@niflheim-x.com](mailto:enterprise@niflheim-x.com)

**Happy building with Niflheim-X! 🚀**