"""
Multi-agent orchestration for coordinated conversations.

This module provides classes for managing conversations between multiple agents,
enabling collaborative problem-solving and specialized task delegation.
"""

import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from .agent import Agent
from .types import Message, MessageRole, AgentResponse


@dataclass
class ConversationTurn:
    """Represents a single turn in a multi-agent conversation.
    
    Attributes:
        agent_name: Name of the agent that spoke
        message: The message content
        response: Full response from the agent
        turn_number: Order of this turn in the conversation
    """
    agent_name: str
    message: str
    response: AgentResponse
    turn_number: int


class AgentOrchestrator:
    """Orchestrates conversations between multiple agents.
    
    The orchestrator manages turn-taking, message routing, and conversation
    flow between multiple specialized agents.
    
    Attributes:
        agents: Dictionary mapping agent names to Agent instances
        conversation_history: History of all conversation turns
        current_speaker: Name of the agent that should speak next
    """
    
    def __init__(self, agents: List[Agent], orchestration_strategy: str = "round_robin"):
        """Initialize the orchestrator.
        
        Args:
            agents: List of agents to orchestrate
            orchestration_strategy: Strategy for managing turns ("round_robin", "topic_based")
        """
        self.agents = {agent.name: agent for agent in agents}
        self.conversation_history: List[ConversationTurn] = []
        self.orchestration_strategy = orchestration_strategy
        self.current_speaker_index = 0
        
        if not self.agents:
            raise ValueError("At least one agent is required")
    
    async def discuss(
        self, 
        initial_prompt: str, 
        rounds: int = 3,
        facilitator_prompt: Optional[str] = None
    ) -> List[ConversationTurn]:
        """Start a discussion between agents.
        
        Args:
            initial_prompt: The topic or question to discuss
            rounds: Number of conversation rounds
            facilitator_prompt: Optional prompt for guiding the discussion
            
        Returns:
            List of conversation turns
        """
        agent_list = list(self.agents.values())
        
        # Clear previous conversation history
        self.conversation_history = []
        
        # Start with the first agent responding to the initial prompt
        current_prompt = initial_prompt
        
        for round_num in range(rounds):
            for agent_idx, agent in enumerate(agent_list):
                turn_number = round_num * len(agent_list) + agent_idx + 1
                
                # Create context from previous turns
                if self.conversation_history:
                    context_messages = self._build_context_for_agent(agent, current_prompt)
                    # Combine context with current prompt
                    full_prompt = f"{current_prompt}\n\nPrevious discussion:\n{context_messages}"
                else:
                    full_prompt = current_prompt
                
                # Generate response from current agent
                response = await agent.chat(full_prompt)
                
                # Ensure we have an AgentResponse object
                if not isinstance(response, AgentResponse):
                    # This shouldn't happen with our current implementation, but safety check
                    raise TypeError(f"Expected AgentResponse, got {type(response)}")
                
                # Record the turn
                turn = ConversationTurn(
                    agent_name=agent.name,
                    message=full_prompt,
                    response=response,
                    turn_number=turn_number
                )
                self.conversation_history.append(turn)
                
                # Update prompt for next agent based on this response
                current_prompt = f"Respond to {agent.name}'s point: {response.content}"
        
        return self.conversation_history
    
    def _build_context_for_agent(self, current_agent: Agent, prompt: str) -> str:
        """Build conversation context for an agent.
        
        Args:
            current_agent: The agent that will receive the context
            prompt: Current prompt
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Get last few turns for context
        recent_turns = self.conversation_history[-3:]  # Last 3 turns for context
        
        for turn in recent_turns:
            context_parts.append(f"{turn.agent_name}: {turn.response.content}")
        
        return "\n".join(context_parts)
    
    async def collaborate(
        self, 
        task: str,
        coordinator_agent: Optional[str] = None
    ) -> AgentResponse:
        """Have agents collaborate on a specific task.
        
        Args:
            task: The task for agents to collaborate on
            coordinator_agent: Name of agent to coordinate (optional)
            
        Returns:
            Final collaborative response
        """
        if coordinator_agent and coordinator_agent not in self.agents:
            raise ValueError(f"Coordinator agent '{coordinator_agent}' not found")
        
        # If no coordinator specified, use the first agent
        coordinator = self.agents[coordinator_agent] if coordinator_agent else list(self.agents.values())[0]
        
        # Step 1: Have coordinator break down the task
        breakdown_prompt = f"""
        As the coordinator, break down this task into subtasks that can be handled by our team:
        Task: {task}
        
        Available team members: {', '.join(self.agents.keys())}
        
        Provide a plan with specific subtasks for each team member.
        """
        
        plan_response = await coordinator.chat(breakdown_prompt)
        
        # Ensure we have an AgentResponse object
        if not isinstance(plan_response, AgentResponse):
            raise TypeError(f"Expected AgentResponse, got {type(plan_response)}")
        
        # Step 2: Execute subtasks with different agents
        subtask_results = []
        
        for agent_name, agent in self.agents.items():
            if agent_name == coordinator.name:
                continue  # Skip coordinator for subtasks
            
            subtask_prompt = f"""
            Based on this plan: {plan_response.content}
            
            Focus on the parts relevant to your expertise and provide your contribution to: {task}
            """
            
            result = await agent.chat(subtask_prompt)
            if not isinstance(result, AgentResponse):
                raise TypeError(f"Expected AgentResponse, got {type(result)}")
            subtask_results.append(f"{agent_name}: {result.content}")
        
        # Step 3: Have coordinator synthesize results
        synthesis_prompt = f"""
        Here are the contributions from the team for the task: {task}
        
        Team contributions:
        {chr(10).join(subtask_results)}
        
        Your plan was: {plan_response.content}
        
        Now synthesize these contributions into a final, comprehensive response.
        """
        
        final_response = await coordinator.chat(synthesis_prompt)
        if not isinstance(final_response, AgentResponse):
            raise TypeError(f"Expected AgentResponse, got {type(final_response)}")
        return final_response
    
    async def moderate_discussion(
        self,
        topic: str,
        max_turns: int = 10,
        convergence_threshold: float = 0.8
    ) -> Tuple[List[ConversationTurn], bool]:
        """Moderate a discussion until consensus or max turns.
        
        Args:
            topic: Discussion topic
            max_turns: Maximum number of turns
            convergence_threshold: Similarity threshold for consensus (0-1)
            
        Returns:
            Tuple of (conversation_history, reached_consensus)
        """
        self.conversation_history = []
        reached_consensus = False
        
        agent_list = list(self.agents.values())
        current_prompt = topic
        
        for turn_num in range(max_turns):
            agent = agent_list[turn_num % len(agent_list)]
            
            # Build context for current agent
            if self.conversation_history:
                context = self._build_context_for_agent(agent, current_prompt)
                full_prompt = f"{topic}\n\nCurrent discussion:\n{context}\n\nYour response:"
            else:
                full_prompt = f"Let's discuss: {topic}\n\nShare your initial thoughts:"
            
            # Generate response
            response = await agent.chat(full_prompt)
            if not isinstance(response, AgentResponse):
                raise TypeError(f"Expected AgentResponse, got {type(response)}")
            
            # Record turn
            turn = ConversationTurn(
                agent_name=agent.name,
                message=full_prompt,
                response=response,
                turn_number=turn_num + 1
            )
            self.conversation_history.append(turn)
            
            # Check for consensus (simplified - in practice you'd use embeddings or NLP)
            if len(self.conversation_history) >= len(agent_list):
                consensus_check = await self._check_consensus()
                if consensus_check:
                    reached_consensus = True
                    break
            
            # Update prompt for next turn
            current_prompt = f"Respond to the ongoing discussion about: {topic}"
        
        return self.conversation_history, reached_consensus
    
    async def _check_consensus(self) -> bool:
        """Check if agents have reached consensus (simplified implementation).
        
        Returns:
            True if consensus detected, False otherwise
        """
        # This is a simplified implementation
        # In practice, you'd use semantic similarity, sentiment analysis, etc.
        
        if len(self.conversation_history) < len(self.agents):
            return False
        
        # Get last response from each agent
        recent_responses = {}
        for turn in reversed(self.conversation_history):
            if turn.agent_name not in recent_responses:
                recent_responses[turn.agent_name] = turn.response.content
            
            if len(recent_responses) == len(self.agents):
                break
        
        # Simple heuristic: check for agreement keywords
        agreement_keywords = ["agree", "consensus", "correct", "yes", "exactly", "I concur"]
        
        agreement_count = 0
        for response in recent_responses.values():
            if any(keyword in response.lower() for keyword in agreement_keywords):
                agreement_count += 1
        
        # Consider consensus if majority agrees
        return agreement_count >= len(self.agents) * 0.6
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the conversation.
        
        Returns:
            Dictionary with conversation statistics
        """
        if not self.conversation_history:
            return {"total_turns": 0, "agents_participated": 0}
        
        agent_turn_counts = {}
        for turn in self.conversation_history:
            agent_turn_counts[turn.agent_name] = agent_turn_counts.get(turn.agent_name, 0) + 1
        
        return {
            "total_turns": len(self.conversation_history),
            "agents_participated": len(agent_turn_counts),
            "turn_distribution": agent_turn_counts,
            "average_turns_per_agent": len(self.conversation_history) / len(agent_turn_counts) if agent_turn_counts else 0
        }
    
    async def export_conversation(self, format: str = "text") -> str:
        """Export conversation history in specified format.
        
        Args:
            format: Export format ("text", "json", "markdown")
            
        Returns:
            Formatted conversation string
        """
        if format == "text":
            lines = []
            for turn in self.conversation_history:
                lines.append(f"Turn {turn.turn_number} - {turn.agent_name}:")
                lines.append(f"  {turn.response.content}")
                lines.append("")
            return "\n".join(lines)
        
        elif format == "markdown":
            lines = ["# Agent Conversation", ""]
            for turn in self.conversation_history:
                lines.append(f"## Turn {turn.turn_number}: {turn.agent_name}")
                lines.append(f"{turn.response.content}")
                lines.append("")
            return "\n".join(lines)
        
        elif format == "json":
            import json
            conversation_data = []
            for turn in self.conversation_history:
                conversation_data.append({
                    "turn_number": turn.turn_number,
                    "agent_name": turn.agent_name,
                    "content": turn.response.content,
                    "metadata": turn.response.metadata
                })
            return json.dumps(conversation_data, indent=2)
        
        else:
            raise ValueError(f"Unsupported format: {format}")


class DebateOrchestrator(AgentOrchestrator):
    """Specialized orchestrator for structured debates.
    
    Manages formal debate structure with opening statements, rebuttals,
    and closing arguments between agents with opposing viewpoints.
    """
    
    def __init__(self, agent_pro: Agent, agent_con: Agent, moderator: Optional[Agent] = None):
        """Initialize debate orchestrator.
        
        Args:
            agent_pro: Agent arguing for the proposition
            agent_con: Agent arguing against the proposition
            moderator: Optional moderator agent
        """
        agents = [agent_pro, agent_con]
        if moderator:
            agents.append(moderator)
        
        super().__init__(agents)
        self.agent_pro = agent_pro
        self.agent_con = agent_con
        self.moderator = moderator
    
    async def conduct_debate(
        self, 
        proposition: str,
        rounds: int = 3
    ) -> List[ConversationTurn]:
        """Conduct a structured debate.
        
        Args:
            proposition: The proposition to debate
            rounds: Number of debate rounds
            
        Returns:
            List of all debate turns
        """
        self.conversation_history = []
        turn_number = 1
        
        # Opening statements
        pro_opening = await self.agent_pro.chat(
            f"Give your opening statement arguing FOR this proposition: {proposition}"
        )
        if not isinstance(pro_opening, AgentResponse):
            raise TypeError(f"Expected AgentResponse, got {type(pro_opening)}")
        self.conversation_history.append(ConversationTurn(
            agent_name=self.agent_pro.name,
            message="Opening statement (PRO)",
            response=pro_opening,
            turn_number=turn_number
        ))
        turn_number += 1
        
        con_opening = await self.agent_con.chat(
            f"Give your opening statement arguing AGAINST this proposition: {proposition}"
        )
        if not isinstance(con_opening, AgentResponse):
            raise TypeError(f"Expected AgentResponse, got {type(con_opening)}")
        self.conversation_history.append(ConversationTurn(
            agent_name=self.agent_con.name,
            message="Opening statement (CON)",
            response=con_opening,
            turn_number=turn_number
        ))
        turn_number += 1
        
        # Debate rounds (rebuttals)
        for round_num in range(rounds):
            # Pro rebuttal
            pro_rebuttal = await self.agent_pro.chat(
                f"Provide a rebuttal to the CON side's arguments. "
                f"Their latest argument: {con_opening.content if round_num == 0 else self.conversation_history[-1].response.content}"
            )
            if not isinstance(pro_rebuttal, AgentResponse):
                raise TypeError(f"Expected AgentResponse, got {type(pro_rebuttal)}")
            self.conversation_history.append(ConversationTurn(
                agent_name=self.agent_pro.name,
                message=f"Rebuttal round {round_num + 1} (PRO)",
                response=pro_rebuttal,
                turn_number=turn_number
            ))
            turn_number += 1
            
            # Con rebuttal  
            con_rebuttal = await self.agent_con.chat(
                f"Provide a rebuttal to the PRO side's arguments. "
                f"Their latest argument: {pro_rebuttal.content}"
            )
            if not isinstance(con_rebuttal, AgentResponse):
                raise TypeError(f"Expected AgentResponse, got {type(con_rebuttal)}")
            self.conversation_history.append(ConversationTurn(
                agent_name=self.agent_con.name,
                message=f"Rebuttal round {round_num + 1} (CON)",
                response=con_rebuttal,
                turn_number=turn_number
            ))
            turn_number += 1
        
        # Closing statements
        pro_closing = await self.agent_pro.chat(
            f"Give your closing statement summarizing your position FOR: {proposition}"
        )
        if not isinstance(pro_closing, AgentResponse):
            raise TypeError(f"Expected AgentResponse, got {type(pro_closing)}")
        self.conversation_history.append(ConversationTurn(
            agent_name=self.agent_pro.name,
            message="Closing statement (PRO)",
            response=pro_closing,
            turn_number=turn_number
        ))
        turn_number += 1
        
        con_closing = await self.agent_con.chat(
            f"Give your closing statement summarizing your position AGAINST: {proposition}"
        )
        if not isinstance(con_closing, AgentResponse):
            raise TypeError(f"Expected AgentResponse, got {type(con_closing)}")
        self.conversation_history.append(ConversationTurn(
            agent_name=self.agent_con.name,
            message="Closing statement (CON)",
            response=con_closing,
            turn_number=turn_number
        ))
        
        # Optional moderator summary
        if self.moderator:
            summary_prompt = f"""
            As the moderator, provide a balanced summary of this debate on: {proposition}
            
            Include key arguments from both sides and note the strongest points made.
            """
            moderator_summary = await self.moderator.chat(summary_prompt)
            if not isinstance(moderator_summary, AgentResponse):
                raise TypeError(f"Expected AgentResponse, got {type(moderator_summary)}")
            self.conversation_history.append(ConversationTurn(
                agent_name=self.moderator.name,
                message="Moderator summary",
                response=moderator_summary,
                turn_number=turn_number + 1
            ))
        
        return self.conversation_history
