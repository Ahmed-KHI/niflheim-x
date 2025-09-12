"""
Enterprise Observability Module for Niflheim-X

Provides comprehensive monitoring, metrics, and observability features
for production AI agent deployments.
"""

import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, AsyncIterator
from datetime import datetime
import asyncio
import json

from ..core.types import Message, MessageRole, AgentResponse, ToolCall, ToolResult


@dataclass
class MetricEvent:
    """Represents a metric event for observability."""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TraceSpan:
    """Represents a trace span for distributed tracing."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "in_progress"  # in_progress, success, error


class MetricsCollector:
    """Collects and exports metrics for agent performance monitoring."""
    
    def __init__(self, export_interval: int = 60):
        self.metrics: List[MetricEvent] = []
        self.export_interval = export_interval
        self._running = False
    
    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a metric event."""
        metric = MetricEvent(
            name=name,
            value=value,
            timestamp=datetime.now(),
            labels=labels or {}
        )
        self.metrics.append(metric)
    
    def record_agent_response_time(self, agent_name: str, duration_ms: float):
        """Record agent response time metric."""
        self.record_metric(
            "agent_response_time_ms",
            duration_ms,
            {"agent_name": agent_name}
        )
    
    def record_tool_execution_time(self, tool_name: str, duration_ms: float, success: bool):
        """Record tool execution time and success rate."""
        self.record_metric(
            "tool_execution_time_ms", 
            duration_ms,
            {"tool_name": tool_name, "success": str(success)}
        )
    
    def record_token_usage(self, model: str, prompt_tokens: int, completion_tokens: int):
        """Record LLM token usage metrics."""
        self.record_metric("tokens_used", prompt_tokens + completion_tokens, {
            "model": model,
            "type": "total"
        })
        self.record_metric("tokens_used", prompt_tokens, {
            "model": model,
            "type": "prompt"
        })
        self.record_metric("tokens_used", completion_tokens, {
            "model": model,
            "type": "completion"
        })
    
    async def export_to_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        # Group metrics by name
        metrics_by_name = {}
        for metric in self.metrics:
            if metric.name not in metrics_by_name:
                metrics_by_name[metric.name] = []
            metrics_by_name[metric.name].append(metric)
        
        for name, metric_list in metrics_by_name.items():
            # Add metric help and type
            lines.append(f"# HELP {name} Agent framework metric")
            lines.append(f"# TYPE {name} gauge")
            
            for metric in metric_list:
                labels_str = ""
                if metric.labels:
                    label_pairs = [f'{k}="{v}"' for k, v in metric.labels.items()]
                    labels_str = "{" + ",".join(label_pairs) + "}"
                
                lines.append(f"{name}{labels_str} {metric.value}")
        
        return "\n".join(lines)


class DistributedTracer:
    """Distributed tracing for multi-agent workflows."""
    
    def __init__(self):
        self.active_spans: Dict[str, TraceSpan] = {}
        self.completed_spans: List[TraceSpan] = []
    
    def start_span(self, operation_name: str, parent_span_id: Optional[str] = None) -> TraceSpan:
        """Start a new trace span."""
        span = TraceSpan(
            trace_id=str(uuid.uuid4()),
            span_id=str(uuid.uuid4()),
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=datetime.now()
        )
        self.active_spans[span.span_id] = span
        return span
    
    def finish_span(self, span_id: str, status: str = "success", error: Optional[str] = None):
        """Finish a trace span."""
        if span_id in self.active_spans:
            span = self.active_spans.pop(span_id)
            span.end_time = datetime.now()
            span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
            span.status = status
            
            if error:
                span.logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "error",
                    "message": error
                })
            
            self.completed_spans.append(span)
    
    def add_span_tag(self, span_id: str, key: str, value: str):
        """Add a tag to an active span."""
        if span_id in self.active_spans:
            self.active_spans[span_id].tags[key] = value
    
    @asynccontextmanager
    async def trace_operation(self, operation_name: str, parent_span_id: Optional[str] = None):
        """Context manager for tracing operations."""
        span = self.start_span(operation_name, parent_span_id)
        try:
            yield span
            self.finish_span(span.span_id, "success")
        except Exception as e:
            self.finish_span(span.span_id, "error", str(e))
            raise


class ObservabilityManager:
    """Central manager for all observability features."""
    
    def __init__(self, 
                 enable_metrics: bool = True,
                 enable_tracing: bool = True,
                 enable_logging: bool = True):
        self.enable_metrics = enable_metrics
        self.enable_tracing = enable_tracing
        self.enable_logging = enable_logging
        
        self.metrics = MetricsCollector() if enable_metrics else None
        self.tracer = DistributedTracer() if enable_tracing else None
    
    async def track_agent_interaction(self, agent_name: str, message: Message, response: AgentResponse):
        """Track a complete agent interaction."""
        if self.metrics:
            # Record response time (you'd measure this in the actual agent)
            # self.metrics.record_agent_response_time(agent_name, response_time_ms)
            
            # Record token usage if available
            if response.usage:
                self.metrics.record_token_usage(
                    "unknown",  # You'd get this from the LLM adapter
                    response.usage.get("prompt_tokens", 0),
                    response.usage.get("completion_tokens", 0)
                )
    
    async def track_tool_execution(self, tool_name: str, tool_call: ToolCall, result: ToolResult):
        """Track tool execution metrics."""
        if self.metrics:
            success = result.error is None
            self.metrics.record_tool_execution_time(
                tool_name, 
                result.execution_time * 1000,  # Convert to ms
                success
            )
    
    async def export_metrics(self) -> Dict[str, Any]:
        """Export all collected metrics."""
        if not self.metrics:
            return {}
        
        return {
            "prometheus": await self.metrics.export_to_prometheus(),
            "raw_metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "timestamp": m.timestamp.isoformat(),
                    "labels": m.labels
                }
                for m in self.metrics.metrics
            ]
        }
    
    async def get_trace_data(self) -> List[Dict[str, Any]]:
        """Get trace data for analysis."""
        if not self.tracer:
            return []
        
        return [
            {
                "trace_id": span.trace_id,
                "span_id": span.span_id,
                "parent_span_id": span.parent_span_id,
                "operation_name": span.operation_name,
                "start_time": span.start_time.isoformat(),
                "end_time": span.end_time.isoformat() if span.end_time else None,
                "duration_ms": span.duration_ms,
                "status": span.status,
                "tags": span.tags,
                "logs": span.logs
            }
            for span in self.tracer.completed_spans
        ]


# Integration with existing Agent class
class ObservableAgent:
    """Enhanced Agent with built-in observability."""
    
    def __init__(self, base_agent, observability_manager: ObservabilityManager):
        self.agent = base_agent
        self.observability = observability_manager
    
    async def chat(self, message: str) -> AgentResponse:
        """Chat with observability tracking."""
        start_time = time.time()
        
        # Start tracing if enabled
        trace_context = None
        if self.observability.tracer:
            trace_context = self.observability.tracer.trace_operation(
                f"agent_chat_{self.agent.name}"
            )
            span = await trace_context.__aenter__()
            span.tags["agent_name"] = self.agent.name
            span.tags["message_length"] = str(len(message))
        
        try:
            # Execute the actual chat
            response = await self.agent.chat(message)
            
            # Track metrics
            if self.observability.metrics:
                duration_ms = (time.time() - start_time) * 1000
                self.observability.metrics.record_agent_response_time(
                    self.agent.name, 
                    duration_ms
                )
            
            # Track the interaction
            user_message = Message(role=MessageRole.USER, content=message)
            await self.observability.track_agent_interaction(
                self.agent.name, 
                user_message, 
                response
            )
            
            return response
            
        except Exception as e:
            if trace_context:
                await trace_context.__aexit__(type(e), e, e.__traceback__)
            raise
        finally:
            if trace_context:
                await trace_context.__aexit__(None, None, None)


# Example usage
async def example_observability():
    """Example of using observability features."""
    # Set up observability
    observability = ObservabilityManager(
        enable_metrics=True,
        enable_tracing=True,
        enable_logging=True
    )
    
    # Wrap your existing agent
    # observable_agent = ObservableAgent(your_agent, observability)
    
    # Use the agent normally
    # response = await observable_agent.chat("Hello!")
    
    # Export metrics for monitoring
    metrics_data = await observability.export_metrics()
    print("Prometheus metrics:")
    print(metrics_data["prometheus"])
    
    # Get trace data
    traces = await observability.get_trace_data()
    print(f"Collected {len(traces)} trace spans")