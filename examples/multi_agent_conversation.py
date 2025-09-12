"""
Multi-agent conversation demo.

This example demonstrates agent orchestration with multiple specialized agents
collaborating and debating on various topics.
"""

import asyncio
import os

from niflheim_x import Agent, OpenAIAdapter, AgentOrchestrator


async def create_specialist_agents():
    """Create a team of specialist agents."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return None
    
    # Create LLM adapter
    llm_config = {
        "api_key": api_key,
        "model": "gpt-4o-mini",
        "temperature": 0.7
    }
    
    # Research Specialist
    researcher = Agent(
        llm=OpenAIAdapter(**llm_config),
        name="Dr. Research",
        system_prompt="""You are Dr. Research, a thorough research specialist. 
        You approach problems analytically, cite evidence, and prefer data-driven solutions.
        You're detail-oriented and always consider multiple perspectives before reaching conclusions."""
    )
    
    # Creative Thinker
    creative = Agent(
        llm=OpenAIAdapter(**llm_config),
        name="Alex Creative", 
        system_prompt="""You are Alex Creative, an innovative creative thinker.
        You think outside the box, propose unconventional solutions, and see possibilities others miss.
        You love brainstorming and aren't afraid to suggest bold, imaginative ideas."""
    )
    
    # Practical Problem Solver
    pragmatist = Agent(
        llm=OpenAIAdapter(**llm_config),
        name="Sam Practical",
        system_prompt="""You are Sam Practical, a results-oriented problem solver.
        You focus on what works in the real world, consider constraints like budget and time,
        and prefer simple, proven solutions over complex theoretical approaches."""
    )
    
    # Critical Analyzer
    critic = Agent(
        llm=OpenAIAdapter(**llm_config),
        name="Chris Critic",
        system_prompt="""You are Chris Critic, a sharp critical thinker.
        You identify potential problems, challenge assumptions, and play devil's advocate.
        You help teams avoid pitfalls by pointing out weaknesses in plans and ideas."""
    )
    
    return [researcher, creative, pragmatist, critic]


async def collaboration_demo():
    """Demonstrate agents collaborating on a complex task."""
    agents = await create_specialist_agents()
    if not agents:
        return
    
    orchestrator = AgentOrchestrator(agents)
    
    print("🤝 Multi-Agent Collaboration Demo")
    print("=" * 50)
    
    task = """
    Our startup needs to create a mobile app that helps people reduce food waste.
    We need to brainstorm features, consider technical constraints, identify potential
    problems, and create an actionable plan for development.
    """
    
    print(f"📋 Task: {task}")
    print("\n🚀 Starting collaboration...")
    print("-" * 50)
    
    # Have agents collaborate
    result = await orchestrator.collaborate(
        task=task,
        coordinator_agent="Dr. Research"  # Research agent will coordinate
    )
    
    print(f"\n🎯 Final Collaborative Result:")
    print(f"Coordinator: {result.metadata.get('agent_name', 'Dr. Research')}")
    print(f"Response: {result.content}")
    
    # Show collaboration statistics
    stats = orchestrator.get_conversation_summary()
    print(f"\n📊 Collaboration Stats:")
    print(f"Total interactions: {stats['total_turns']}")
    print(f"Agents participated: {stats['agents_participated']}")


async def discussion_demo():
    """Demonstrate a structured discussion between agents."""
    agents = await create_specialist_agents()
    if not agents:
        return
    
    orchestrator = AgentOrchestrator(agents)
    
    print("\n💬 Multi-Agent Discussion Demo")
    print("=" * 50)
    
    topic = "Should companies prioritize remote work or return to office?"
    
    print(f"🎯 Discussion Topic: {topic}")
    print("\n🗣️  Starting discussion...")
    print("-" * 50)
    
    # Conduct discussion
    conversation = await orchestrator.discuss(
        initial_prompt=topic,
        rounds=2  # 2 rounds of discussion
    )
    
    print("\n📝 Discussion Summary:")
    for turn in conversation:
        print(f"\n{turn.agent_name} (Turn {turn.turn_number}):")
        print(f"  {turn.response.content[:200]}{'...' if len(turn.response.content) > 200 else ''}")
    
    # Export conversation
    markdown_export = await orchestrator.export_conversation(format="markdown")
    with open("discussion_export.md", "w", encoding="utf-8") as f:
        f.write(markdown_export)
    print(f"\n💾 Full conversation exported to discussion_export.md")


async def debate_demo():
    """Demonstrate a structured debate between two agents."""
    agents = await create_specialist_agents()
    if not agents:
        return
    
    from niflheim_x.core.orchestrator import DebateOrchestrator
    
    print("\n⚖️  Structured Debate Demo")
    print("=" * 50)
    
    # Create debate orchestrator with opposing agents
    debate_orchestrator = DebateOrchestrator(
        agent_pro=agents[1],  # Alex Creative (pro)
        agent_con=agents[3],  # Chris Critic (con)
        moderator=agents[0]   # Dr. Research (moderator)
    )
    
    proposition = "Artificial Intelligence will create more jobs than it eliminates"
    
    print(f"🎯 Debate Proposition: {proposition}")
    print(f"👍 PRO: {agents[1].name}")
    print(f"👎 CON: {agents[3].name}")
    print(f"⚖️  Moderator: {agents[0].name}")
    print("\n🗣️  Starting debate...")
    print("-" * 50)
    
    # Conduct debate
    debate_turns = await debate_orchestrator.conduct_debate(
        proposition=proposition,
        rounds=2
    )
    
    print("\n📝 Debate Summary:")
    for turn in debate_turns:
        print(f"\n{turn.message} - {turn.agent_name}:")
        print(f"  {turn.response.content[:300]}{'...' if len(turn.response.content) > 300 else ''}")
    
    # Export debate
    debate_export = await debate_orchestrator.export_conversation(format="markdown")
    with open("debate_export.md", "w", encoding="utf-8") as f:
        f.write(debate_export)
    print(f"\n💾 Full debate exported to debate_export.md")


async def interactive_multi_agent():
    """Interactive multi-agent session where user can ask questions."""
    agents = await create_specialist_agents()
    if not agents:
        return
    
    orchestrator = AgentOrchestrator(agents)
    
    print("\n🎪 Interactive Multi-Agent Session")
    print("=" * 50)
    
    print("Meet your team of specialists:")
    for agent in agents:
        print(f"  • {agent.name}: {agent.config.system_prompt[:100]}...")
    
    print("\nAsk any question and the team will collaborate to give you a comprehensive answer!")
    print("Type 'quit' to exit.")
    print("-" * 50)
    
    while True:
        try:
            question = input("\n🙋 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Session ended!")
                break
            
            if not question:
                continue
            
            print("\n🤔 Team is collaborating...")
            
            # Have the team collaborate on the answer
            result = await orchestrator.collaborate(
                task=f"User question: {question}",
                coordinator_agent="Dr. Research"
            )
            
            print(f"\n🎯 Team Response:")
            print(f"{result.content}")
            
            print("-" * 50)
        
        except KeyboardInterrupt:
            print("\n👋 Session ended!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("Choose a demo:")
    print("1. Collaboration Demo (team working on a task)")
    print("2. Discussion Demo (open discussion)")
    print("3. Debate Demo (structured debate)")
    print("4. Interactive Session (ask the team questions)")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        asyncio.run(collaboration_demo())
    elif choice == "2":
        asyncio.run(discussion_demo())
    elif choice == "3":
        asyncio.run(debate_demo())
    elif choice == "4":
        asyncio.run(interactive_multi_agent())
    else:
        print("Invalid choice. Running collaboration demo...")
        asyncio.run(collaboration_demo())
