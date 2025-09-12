"""
Advanced Workflow Engine for Multi-Agent Orchestration

Provides visual workflow design, conditional logic, parallel execution,
and enterprise-grade workflow management capabilities.
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable, AsyncIterator
from enum import Enum
from datetime import datetime
import json

from ..core.agent import Agent
from ..core.types import Message, AgentResponse


class WorkflowStepType(str, Enum):
    """Types of workflow steps."""
    AGENT = "agent"
    TOOL = "tool"
    CONDITION = "condition"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    HUMAN_INPUT = "human_input"
    DATA_TRANSFORM = "data_transform"
    DELAY = "delay"


class WorkflowStepStatus(str, Enum):
    """Status of workflow step execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""
    id: str
    name: str
    type: WorkflowStepType
    config: Dict[str, Any] = field(default_factory=dict)
    next_steps: List[str] = field(default_factory=list)
    condition: Optional[str] = None  # JavaScript-like expression
    timeout_seconds: Optional[int] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Tracks the execution of a workflow."""
    id: str
    workflow_id: str
    status: WorkflowStepStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    current_step: Optional[str] = None
    step_results: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class Workflow:
    """Defines a complete workflow with multiple steps."""
    id: str
    name: str
    description: str
    version: str
    steps: Dict[str, WorkflowStep] = field(default_factory=dict)
    entry_point: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_step(self, step: WorkflowStep) -> "Workflow":
        """Add a step to the workflow."""
        self.steps[step.id] = step
        if not self.entry_point:
            self.entry_point = step.id
        return self
    
    def connect_steps(self, from_step: str, to_step: str) -> "Workflow":
        """Connect two steps in the workflow."""
        if from_step in self.steps:
            self.steps[from_step].next_steps.append(to_step)
        return self


class ConditionEvaluator:
    """Evaluates conditions for workflow branching."""
    
    @staticmethod
    def evaluate(condition: str, variables: Dict[str, Any]) -> bool:
        """Evaluate a condition expression safely."""
        # Simple condition evaluation - in production, use a safer expression evaluator
        # This is a simplified example
        try:
            # Replace variables in the condition
            for var_name, var_value in variables.items():
                if isinstance(var_value, str):
                    condition = condition.replace(f"${var_name}", f'"{var_value}"')
                else:
                    condition = condition.replace(f"${var_name}", str(var_value))
            
            # Basic safety check - only allow simple comparisons
            allowed_operators = ['==', '!=', '<', '>', '<=', '>=', 'and', 'or', 'not', 'in']
            if any(op in condition for op in ['import', 'exec', 'eval', '__']):
                raise ValueError("Unsafe condition expression")
            
            return eval(condition, {"__builtins__": {}}, {})
        except Exception as e:
            print(f"Condition evaluation error: {e}")
            return False


class WorkflowEngine:
    """Executes workflows with multi-agent coordination."""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.step_handlers: Dict[WorkflowStepType, Callable] = {
            WorkflowStepType.AGENT: self._execute_agent_step,
            WorkflowStepType.TOOL: self._execute_tool_step,
            WorkflowStepType.CONDITION: self._execute_condition_step,
            WorkflowStepType.PARALLEL: self._execute_parallel_step,
            WorkflowStepType.SEQUENTIAL: self._execute_sequential_step,
            WorkflowStepType.HUMAN_INPUT: self._execute_human_input_step,
            WorkflowStepType.DATA_TRANSFORM: self._execute_data_transform_step,
            WorkflowStepType.DELAY: self._execute_delay_step,
        }
    
    def register_agent(self, name: str, agent: Agent):
        """Register an agent for use in workflows."""
        self.agents[name] = agent
    
    def register_workflow(self, workflow: Workflow):
        """Register a workflow definition."""
        self.workflows[workflow.id] = workflow
    
    async def execute_workflow(self, 
                              workflow_id: str, 
                              input_data: Optional[Dict[str, Any]] = None) -> WorkflowExecution:
        """Execute a workflow and return the execution record."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        execution = WorkflowExecution(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            status=WorkflowStepStatus.RUNNING,
            start_time=datetime.now(),
            variables=input_data or {}
        )
        
        self.executions[execution.id] = execution
        
        try:
            await self._execute_step(workflow, execution, workflow.entry_point)
            execution.status = WorkflowStepStatus.COMPLETED
        except Exception as e:
            execution.status = WorkflowStepStatus.FAILED
            execution.error_message = str(e)
        finally:
            execution.end_time = datetime.now()
        
        return execution
    
    async def _execute_step(self, 
                           workflow: Workflow, 
                           execution: WorkflowExecution, 
                           step_id: str):
        """Execute a single workflow step."""
        if step_id not in workflow.steps:
            return
        
        step = workflow.steps[step_id]
        execution.current_step = step_id
        
        # Check condition if present
        if step.condition and not ConditionEvaluator.evaluate(step.condition, execution.variables):
            execution.step_results[step_id] = {"status": "skipped", "reason": "condition_not_met"}
            return await self._execute_next_steps(workflow, execution, step)
        
        # Execute the step
        handler = self.step_handlers.get(step.type)
        if not handler:
            raise ValueError(f"No handler for step type: {step.type}")
        
        try:
            result = await handler(step, execution)
            execution.step_results[step_id] = result
            
            # Execute next steps
            await self._execute_next_steps(workflow, execution, step)
            
        except Exception as e:
            execution.step_results[step_id] = {"status": "failed", "error": str(e)}
            if step.retry_count > 0:
                # Implement retry logic
                pass
            else:
                raise
    
    async def _execute_next_steps(self, 
                                 workflow: Workflow, 
                                 execution: WorkflowExecution, 
                                 current_step: WorkflowStep):
        """Execute the next steps after current step completes."""
        for next_step_id in current_step.next_steps:
            await self._execute_step(workflow, execution, next_step_id)
    
    async def _execute_agent_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Execute an agent step."""
        agent_name = step.config.get("agent_name")
        prompt = step.config.get("prompt", "")
        
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not registered")
        
        # Replace variables in prompt
        for var_name, var_value in execution.variables.items():
            prompt = prompt.replace(f"${{{var_name}}}", str(var_value))
        
        agent = self.agents[agent_name]
        response = await agent.chat(prompt)
        
        # Store result in variables for next steps
        result_var = step.config.get("result_variable", f"step_{step.id}_result")
        execution.variables[result_var] = response.content
        
        return {
            "status": "completed",
            "response": response.content,
            "token_usage": response.usage
        }
    
    async def _execute_tool_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Execute a tool step."""
        tool_name = step.config.get("tool_name")
        tool_args = step.config.get("arguments", {})
        
        # Replace variables in arguments
        for key, value in tool_args.items():
            if isinstance(value, str):
                for var_name, var_value in execution.variables.items():
                    value = value.replace(f"${{{var_name}}}", str(var_value))
                tool_args[key] = value
        
        # Execute tool (this would integrate with your tool system)
        # result = await self.tool_registry.execute_tool(tool_name, tool_args)
        
        return {"status": "completed", "result": "tool_result"}
    
    async def _execute_condition_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Execute a condition step (branching logic)."""
        condition = step.config.get("condition", "true")
        result = ConditionEvaluator.evaluate(condition, execution.variables)
        
        return {"status": "completed", "condition_result": result}
    
    async def _execute_parallel_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Execute multiple steps in parallel."""
        parallel_steps = step.config.get("steps", [])
        
        # Execute all parallel steps concurrently
        tasks = []
        for parallel_step_id in parallel_steps:
            if parallel_step_id in execution.step_results:
                continue  # Skip already executed steps
            task = asyncio.create_task(
                self._execute_step(self.workflows[execution.workflow_id], execution, parallel_step_id)
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        return {"status": "completed", "parallel_steps_completed": len(tasks)}
    
    async def _execute_sequential_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Execute multiple steps in sequence."""
        sequential_steps = step.config.get("steps", [])
        
        for sequential_step_id in sequential_steps:
            await self._execute_step(self.workflows[execution.workflow_id], execution, sequential_step_id)
        
        return {"status": "completed", "sequential_steps_completed": len(sequential_steps)}
    
    async def _execute_human_input_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Execute a human input step (pauses workflow for human intervention)."""
        prompt = step.config.get("prompt", "Human input required")
        input_type = step.config.get("input_type", "text")
        
        # In a real implementation, this would integrate with a UI system
        # For now, we'll just store the requirement and pause
        return {
            "status": "waiting_for_input",
            "prompt": prompt,
            "input_type": input_type
        }
    
    async def _execute_data_transform_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Execute a data transformation step."""
        transform_type = step.config.get("transform_type", "json")
        source_var = step.config.get("source_variable")
        target_var = step.config.get("target_variable")
        
        if source_var in execution.variables and target_var:
            source_data = execution.variables[source_var]
            
            # Apply transformation (simplified example)
            if transform_type == "json_parse":
                transformed_data = json.loads(source_data)
            elif transform_type == "json_stringify":
                transformed_data = json.dumps(source_data)
            else:
                transformed_data = source_data
            
            execution.variables[target_var] = transformed_data
        
        return {"status": "completed", "transform_type": transform_type}
    
    async def _execute_delay_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Execute a delay step."""
        delay_seconds = step.config.get("delay_seconds", 1)
        await asyncio.sleep(delay_seconds)
        
        return {"status": "completed", "delay_seconds": delay_seconds}


# Workflow Builder Helper
class WorkflowBuilder:
    """Helper class for building workflows programmatically."""
    
    def __init__(self, name: str, description: str = ""):
        self.workflow = Workflow(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            version="1.0"
        )
    
    def add_agent_step(self, 
                      step_id: str, 
                      agent_name: str, 
                      prompt: str,
                      result_variable: Optional[str] = None) -> "WorkflowBuilder":
        """Add an agent execution step."""
        step = WorkflowStep(
            id=step_id,
            name=f"Agent: {agent_name}",
            type=WorkflowStepType.AGENT,
            config={
                "agent_name": agent_name,
                "prompt": prompt,
                "result_variable": result_variable or f"{step_id}_result"
            }
        )
        self.workflow.add_step(step)
        return self
    
    def add_condition_step(self, 
                          step_id: str, 
                          condition: str,
                          true_steps: Optional[List[str]] = None,
                          false_steps: Optional[List[str]] = None) -> "WorkflowBuilder":
        """Add a conditional branching step."""
        step = WorkflowStep(
            id=step_id,
            name=f"Condition: {condition}",
            type=WorkflowStepType.CONDITION,
            config={
                "condition": condition,
                "true_steps": true_steps or [],
                "false_steps": false_steps or []
            }
        )
        self.workflow.add_step(step)
        return self
    
    def add_parallel_step(self, 
                         step_id: str, 
                         parallel_steps: List[str]) -> "WorkflowBuilder":
        """Add a parallel execution step."""
        step = WorkflowStep(
            id=step_id,
            name="Parallel Execution",
            type=WorkflowStepType.PARALLEL,
            config={"steps": parallel_steps}
        )
        self.workflow.add_step(step)
        return self
    
    def connect(self, from_step: str, to_step: str) -> "WorkflowBuilder":
        """Connect two steps."""
        self.workflow.connect_steps(from_step, to_step)
        return self
    
    def build(self) -> Workflow:
        """Build and return the workflow."""
        return self.workflow


# Example Usage
async def example_multi_agent_workflow():
    """Example of a complex multi-agent workflow."""
    
    # Create workflow engine
    engine = WorkflowEngine()
    
    # Register agents (you'd create these with your Agent class)
    # engine.register_agent("researcher", research_agent)
    # engine.register_agent("writer", writer_agent)
    # engine.register_agent("reviewer", review_agent)
    
    # Build a workflow
    workflow = (WorkflowBuilder("Content Creation Pipeline", "Multi-agent content creation")
                .add_agent_step(
                    "research", 
                    "researcher", 
                    "Research the topic: ${topic}",
                    "research_results"
                )
                .add_agent_step(
                    "write_draft", 
                    "writer", 
                    "Write an article based on this research: ${research_results}",
                    "draft_content"
                )
                .add_agent_step(
                    "review", 
                    "reviewer", 
                    "Review and improve this content: ${draft_content}",
                    "final_content"
                )
                .connect("research", "write_draft")
                .connect("write_draft", "review")
                .build())
    
    # Register and execute workflow
    engine.register_workflow(workflow)
    
    execution = await engine.execute_workflow(
        workflow.id, 
        {"topic": "The Future of AI Agents"}
    )
    
    print(f"Workflow execution status: {execution.status}")
    print(f"Final content: {execution.variables.get('final_content', 'N/A')}")
    
    return execution