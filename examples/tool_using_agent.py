"""
Tool-using agent example.

This example shows how to register and use tools with an agent,
including a calculator, weather fetcher, and web search.
"""

import asyncio
import json
import os
import random
from datetime import datetime
from typing import Dict, Any

from niflheim_x import Agent, OpenAIAdapter


# Example tool functions
def calculator(expression: str) -> float:
    """Evaluate mathematical expressions safely.
    
    expression: Mathematical expression to evaluate (e.g., "2 + 3 * 4")
    """
    # Simple safe evaluation - only allow basic math operations
    allowed_chars = set("0123456789+-*/()., ")
    if not all(c in allowed_chars for c in expression):
        raise ValueError("Expression contains invalid characters")
    
    try:
        # Use eval with restricted environment for safety
        result = eval(expression, {"__builtins__": {}}, {})
        return float(result)
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")


def get_weather(city: str) -> Dict[str, Any]:
    """Get current weather for a city (mock implementation).
    
    city: Name of the city to get weather for
    """
    # Mock weather data - in production, use a real weather API
    weather_conditions = ["sunny", "cloudy", "rainy", "snowy", "foggy"]
    
    return {
        "city": city,
        "temperature": random.randint(-10, 35),
        "condition": random.choice(weather_conditions),
        "humidity": random.randint(30, 90),
        "wind_speed": random.randint(0, 30),
        "timestamp": datetime.now().isoformat()
    }


def search_web(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Search the web for information (mock implementation).
    
    query: Search query
    max_results: Maximum number of results to return
    """
    # Mock search results - in production, use a real search API
    mock_results = [
        {
            "title": f"Result about {query} - Article 1",
            "url": f"https://example.com/article1?q={query}",
            "snippet": f"This is a comprehensive article about {query} with detailed information..."
        },
        {
            "title": f"{query} - Wikipedia",
            "url": f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
            "snippet": f"Wikipedia article providing encyclopedic information about {query}..."
        },
        {
            "title": f"Latest news about {query}",
            "url": f"https://news.example.com/{query}",
            "snippet": f"Breaking news and updates related to {query}..."
        }
    ]
    
    return {
        "query": query,
        "results": mock_results[:max_results],
        "total_found": len(mock_results),
        "search_time": 0.1
    }


def save_note(title: str, content: str) -> str:
    """Save a note to the local file system.
    
    title: Title of the note
    content: Content of the note
    """
    filename = f"note_{title.replace(' ', '_').lower()}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n")
            f.write(f"Created: {datetime.now().isoformat()}\n")
            f.write(f"Content:\n{content}")
        
        return f"Note saved successfully as {filename}"
    except Exception as e:
        return f"Failed to save note: {e}"


def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def create_tool_agent():
    """Create an agent with registered tools."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return None
    
    # Create agent
    agent = Agent(
        llm=OpenAIAdapter(
            api_key=api_key,
            model="gpt-4o-mini",
            temperature=0.3
        ),
        name="Tool Assistant",
        system_prompt="""You are a helpful assistant with access to various tools. 
        You can help with calculations, weather information, web searches, note-taking, and time queries.
        Always use the appropriate tool when the user asks for something you have a tool for.""",
        memory_backend="dict"
    )
    
    # Register tools using the decorator
    @agent.tool(description="Perform mathematical calculations")
    def calc(expression: str) -> float:
        return calculator(expression)
    
    @agent.tool(description="Get weather information for a city")
    def weather(city: str) -> Dict[str, Any]:
        return get_weather(city)
    
    @agent.tool(description="Search the web for information")  
    def search(query: str, max_results: int = 5) -> Dict[str, Any]:
        return search_web(query, max_results)
    
    @agent.tool(description="Save a note with title and content")
    def note(title: str, content: str) -> str:
        return save_note(title, content)
    
    @agent.tool(description="Get current date and time")
    def time() -> str:
        return get_current_time()
    
    return agent


async def demo_tool_usage():
    """Demonstrate tool usage with various examples."""
    agent = await create_tool_agent()
    if not agent:
        return
    
    print("🛠️  Tool-Using Agent Demo")
    print("=" * 40)
    
    # List available tools
    tools = agent.get_available_tools()
    print(f"\n📋 Available tools: {', '.join(tool.name for tool in tools)}")
    print("-" * 40)
    
    # Example interactions
    examples = [
        "What's 25 * 4 + 15?",
        "What's the weather like in Tokyo?",
        "Search for information about machine learning",
        "Save a note titled 'Meeting Ideas' with content 'Discuss project timeline and budget allocation'",
        "What time is it?",
        "Can you calculate the area of a circle with radius 5? Use 3.14159 for pi.",
        "Search for recent news about artificial intelligence",
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n🔍 Example {i}: {example}")
        print("🤖 Assistant: ", end="", flush=True)
        
        try:
            response = await agent.chat(example)
            print(response.content)
            
            # Show tool calls if any were made
            if response.tool_calls:
                print(f"   🔧 Used tools: {', '.join(tc.name for tc in response.tool_calls)}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)


async def interactive_tool_session():
    """Run an interactive session with the tool agent."""
    agent = await create_tool_agent()
    if not agent:
        return
    
    print("🛠️  Interactive Tool Assistant")
    print("=" * 40)
    
    # Show available tools
    tools = agent.get_available_tools()
    print(f"\n📋 I have access to these tools:")
    for tool in tools:
        print(f"  • {tool.name}: {tool.description}")
    
    print("\nAsk me anything! I'll use the appropriate tools to help you.")
    print("Type 'quit' to exit, 'tools' to see available tools again.")
    print("-" * 40)
    
    while True:
        try:
            user_input = input("\n🙋 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'tools':
                print("\n📋 Available tools:")
                for tool in agent.get_available_tools():
                    print(f"  • {tool.name}: {tool.description}")
                continue
            
            if not user_input:
                continue
            
            print("🤖 Assistant: ", end="", flush=True)
            response = await agent.chat(user_input)
            print(response.content)
            
            # Show which tools were used
            if response.tool_calls:
                print(f"   🔧 Tools used: {', '.join(tc.name for tc in response.tool_calls)}")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("Choose a mode:")
    print("1. Demo Mode (predefined examples)")
    print("2. Interactive Mode")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(demo_tool_usage())
    elif choice == "2":
        asyncio.run(interactive_tool_session())
    else:
        print("Invalid choice. Running demo mode...")
        asyncio.run(demo_tool_usage())
