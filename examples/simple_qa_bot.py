"""
Simple Q&A bot example using Niflheim_x.

This example demonstrates the basics of creating an agent with memory
for conversational question-answering.
"""

import asyncio
import os
from niflheim_x import Agent, OpenAIAdapter


async def main():
    """Run the Q&A bot example."""
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Create an agent with OpenAI
    agent = Agent(
        llm=OpenAIAdapter(
            api_key=api_key,
            model="gpt-4o-mini",
            temperature=0.7
        ),
        name="QA Bot",
        system_prompt="You are a knowledgeable assistant that provides helpful, accurate answers to questions.",
        memory_backend="dict"  # Use in-memory storage
    )
    
    print("🤖 Q&A Bot initialized! Ask me anything (type 'quit' to exit)")
    print("-" * 50)
    
    while True:
        try:
            # Get user input
            question = input("\n🙋 You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            # Get response from agent
            print("🤖 Bot: ", end="", flush=True)
            response = await agent.chat(question)
            print(response.content)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def streaming_example():
    """Example showing streaming responses."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    agent = Agent(
        llm=OpenAIAdapter(api_key=api_key, model="gpt-4o-mini"),
        system_prompt="You are a creative storyteller."
    )
    
    print("📚 Streaming Story Example")
    print("-" * 30)
    
    question = "Tell me a short story about a robot learning to paint"
    print(f"🙋 Question: {question}")
    print("🤖 Story: ", end="", flush=True)
    
    # Stream the response
    async for token in agent.chat_stream(question):
        print(token.content, end="", flush=True)
    
    print("\n\n✨ Story complete!")


if __name__ == "__main__":
    print("Choose an example:")
    print("1. Interactive Q&A Bot")
    print("2. Streaming Story Example")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(main())
    elif choice == "2":
        asyncio.run(streaming_example())
    else:
        print("Invalid choice. Running Q&A bot...")
        asyncio.run(main())
