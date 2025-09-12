"""
Agent-to-Agent (A2A) and Model Context Protocol (MCP) Support

Implements enterprise protocol standards for agent communication
and integration with external systems.
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Union, AsyncIterator, Callable
from datetime import datetime
from abc import ABC, abstractmethod

from ..core.agent import Agent
from ..core.types import Message, AgentResponse


# A2A Protocol Implementation
@dataclass
class A2AMessage:
    """Agent-to-Agent message format."""
    id: str
    sender_id: str
    receiver_id: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    ttl_seconds: Optional[int] = None


@dataclass
class A2ACapability:
    """Describes an agent's capabilities for A2A communication."""
    id: str
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    async_support: bool = True


class A2ATransport(ABC):
    """Abstract transport layer for A2A communication."""
    
    @abstractmethod
    async def send_message(self, message: A2AMessage) -> bool:
        """Send a message to another agent."""
        pass
    
    @abstractmethod
    async def receive_messages(self, agent_id: str) -> AsyncIterator[A2AMessage]:
        """Receive messages from other agents."""
        pass
    
    @abstractmethod
    async def register_agent(self, agent_id: str, capabilities: List[A2ACapability]) -> bool:
        """Register an agent with its capabilities."""
        pass


class InMemoryA2ATransport(A2ATransport):
    """In-memory transport for testing and development."""
    
    def __init__(self):
        self.message_queues: Dict[str, List[A2AMessage]] = {}
        self.agent_capabilities: Dict[str, List[A2ACapability]] = {}
    
    async def send_message(self, message: A2AMessage) -> bool:
        """Send message to recipient's queue."""
        if message.receiver_id not in self.message_queues:
            self.message_queues[message.receiver_id] = []
        
        self.message_queues[message.receiver_id].append(message)
        return True
    
    async def receive_messages(self, agent_id: str) -> AsyncIterator[A2AMessage]:
        """Receive messages for a specific agent."""
        if agent_id not in self.message_queues:
            return
        
        messages = self.message_queues[agent_id].copy()
        self.message_queues[agent_id].clear()
        
        for message in messages:
            yield message
    
    async def register_agent(self, agent_id: str, capabilities: List[A2ACapability]) -> bool:
        """Register agent capabilities."""
        self.agent_capabilities[agent_id] = capabilities
        if agent_id not in self.message_queues:
            self.message_queues[agent_id] = []
        return True
    
    def get_agent_capabilities(self, agent_id: str) -> List[A2ACapability]:
        """Get capabilities for an agent."""
        return self.agent_capabilities.get(agent_id, [])


class A2AAgent:
    """Agent wrapper with A2A protocol support."""
    
    def __init__(self, 
                 agent: Agent, 
                 transport: A2ATransport,
                 capabilities: Optional[List[A2ACapability]] = None):
        self.agent = agent
        self.transport = transport
        self.agent_id = f"agent_{agent.name}_{uuid.uuid4().hex[:8]}"
        self.capabilities = capabilities or []
        self.message_handlers: Dict[str, Callable] = {}
        self._running = False
    
    async def start(self):
        """Start the A2A agent."""
        await self.transport.register_agent(self.agent_id, self.capabilities)
        self._running = True
        
        # Start message processing loop
        asyncio.create_task(self._process_messages())
    
    async def stop(self):
        """Stop the A2A agent."""
        self._running = False
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a handler for specific message types."""
        self.message_handlers[message_type] = handler
    
    async def send_to_agent(self, 
                           receiver_id: str, 
                           message_type: str, 
                           payload: Dict[str, Any],
                           correlation_id: Optional[str] = None) -> bool:
        """Send a message to another agent."""
        message = A2AMessage(
            id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.now(),
            correlation_id=correlation_id
        )
        
        return await self.transport.send_message(message)
    
    async def _process_messages(self):
        """Process incoming messages."""
        while self._running:
            try:
                message_iterator = await self.transport.receive_messages(self.agent_id)
                async for message in message_iterator:
                    await self._handle_message(message)
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
            except Exception as e:
                print(f"Error processing messages: {e}")
    
    async def _handle_message(self, message: A2AMessage):
        """Handle an incoming message."""
        handler = self.message_handlers.get(message.message_type)
        
        if handler:
            try:
                await handler(message)
            except Exception as e:
                # Send error response if reply_to is specified
                if message.reply_to:
                    error_message = A2AMessage(
                        id=str(uuid.uuid4()),
                        sender_id=self.agent_id,
                        receiver_id=message.sender_id,
                        message_type="error",
                        payload={"error": str(e), "original_message_id": message.id},
                        timestamp=datetime.now(),
                        correlation_id=message.correlation_id
                    )
                    await self.transport.send_message(error_message)
        else:
            print(f"No handler for message type: {message.message_type}")


# MCP (Model Context Protocol) Implementation
@dataclass
class MCPResource:
    """MCP Resource definition."""
    uri: str
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MCPTool:
    """MCP Tool definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class MCPPrompt:
    """MCP Prompt template."""
    name: str
    description: str
    arguments: List[Dict[str, Any]]


class MCPServer:
    """Model Context Protocol server implementation."""
    
    def __init__(self, name: str, version: str = "1.0"):
        self.name = name
        self.version = version
        self.resources: Dict[str, MCPResource] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.prompts: Dict[str, MCPPrompt] = {}
        self.resource_handlers: Dict[str, Callable] = {}
        self.tool_handlers: Dict[str, Callable] = {}
    
    def add_resource(self, resource: MCPResource, handler: Callable):
        """Add a resource with its handler."""
        self.resources[resource.uri] = resource
        self.resource_handlers[resource.uri] = handler
    
    def add_tool(self, tool: MCPTool, handler: Callable):
        """Add a tool with its handler."""
        self.tools[tool.name] = tool
        self.tool_handlers[tool.name] = handler
    
    def add_prompt(self, prompt: MCPPrompt):
        """Add a prompt template."""
        self.prompts[prompt.name] = prompt
    
    async def list_resources(self) -> List[MCPResource]:
        """List available resources."""
        return list(self.resources.values())
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource by URI."""
        if uri not in self.resource_handlers:
            raise ValueError(f"Resource not found: {uri}")
        
        handler = self.resource_handlers[uri]
        return await handler(uri)
    
    async def list_tools(self) -> List[MCPTool]:
        """List available tools."""
        return list(self.tools.values())
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool with arguments."""
        if name not in self.tool_handlers:
            raise ValueError(f"Tool not found: {name}")
        
        handler = self.tool_handlers[name]
        return await handler(arguments)
    
    async def list_prompts(self) -> List[MCPPrompt]:
        """List available prompts."""
        return list(self.prompts.values())
    
    async def get_prompt(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> str:
        """Get a prompt with arguments filled in."""
        if name not in self.prompts:
            raise ValueError(f"Prompt not found: {name}")
        
        prompt = self.prompts[name]
        # Simple template substitution (in production, use a proper template engine)
        prompt_text = prompt.description
        
        if arguments:
            for key, value in arguments.items():
                prompt_text = prompt_text.replace(f"{{{key}}}", str(value))
        
        return prompt_text


class MCPClient:
    """Model Context Protocol client implementation."""
    
    def __init__(self, server: MCPServer):
        self.server = server
    
    async def list_resources(self) -> List[MCPResource]:
        """List resources from the server."""
        return await self.server.list_resources()
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource from the server."""
        return await self.server.read_resource(uri)
    
    async def list_tools(self) -> List[MCPTool]:
        """List tools from the server."""
        return await self.server.list_tools()
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the server."""
        return await self.server.call_tool(name, arguments)
    
    async def list_prompts(self) -> List[MCPPrompt]:
        """List prompts from the server."""
        return await self.server.list_prompts()
    
    async def get_prompt(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> str:
        """Get a prompt from the server."""
        return await self.server.get_prompt(name, arguments)


# Integration with existing Niflheim-X Agent
class ProtocolEnabledAgent:
    """Agent with A2A and MCP protocol support."""
    
    def __init__(self, 
                 agent: Agent,
                 a2a_transport: Optional[A2ATransport] = None,
                 mcp_servers: Optional[List[MCPServer]] = None):
        self.agent = agent
        self.a2a_agent = None
        self.mcp_clients: List[MCPClient] = []
        
        if a2a_transport:
            capabilities = [
                A2ACapability(
                    id="chat",
                    name="Chat Capability",
                    description="Process chat messages",
                    input_schema={"type": "object", "properties": {"message": {"type": "string"}}},
                    output_schema={"type": "object", "properties": {"response": {"type": "string"}}}
                )
            ]
            self.a2a_agent = A2AAgent(agent, a2a_transport, capabilities)
            self.a2a_agent.register_message_handler("chat", self._handle_chat_message)
        
        if mcp_servers:
            self.mcp_clients = [MCPClient(server) for server in mcp_servers]
    
    async def start(self):
        """Start protocol support."""
        if self.a2a_agent:
            await self.a2a_agent.start()
    
    async def stop(self):
        """Stop protocol support."""
        if self.a2a_agent:
            await self.a2a_agent.stop()
    
    async def _handle_chat_message(self, message: A2AMessage):
        """Handle incoming chat messages via A2A."""
        chat_text = message.payload.get("message", "")
        response = await self.agent.chat(chat_text)
        
        # Send response back
        if message.reply_to and self.a2a_agent:
            await self.a2a_agent.send_to_agent(
                message.sender_id,
                "chat_response",
                {"response": response.content},
                correlation_id=message.correlation_id
            )
    
    async def get_mcp_resources(self) -> List[MCPResource]:
        """Get all resources from connected MCP servers."""
        all_resources = []
        for client in self.mcp_clients:
            resources = await client.list_resources()
            all_resources.extend(resources)
        return all_resources
    
    async def use_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Use a tool from any connected MCP server."""
        for client in self.mcp_clients:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            
            if tool_name in tool_names:
                return await client.call_tool(tool_name, arguments)
        
        raise ValueError(f"Tool {tool_name} not found in any MCP server")


# Example Usage
async def example_a2a_communication():
    """Example of A2A agent communication."""
    
    # Create transport
    transport = InMemoryA2ATransport()
    
    # Create two agents with A2A support
    # agent1 = ProtocolEnabledAgent(your_agent1, a2a_transport=transport)
    # agent2 = ProtocolEnabledAgent(your_agent2, a2a_transport=transport)
    
    # Start both agents
    # await agent1.start()
    # await agent2.start()
    
    # Agent1 sends message to Agent2
    # await agent1.a2a_agent.send_to_agent(
    #     agent2.a2a_agent.agent_id,
    #     "chat",
    #     {"message": "Hello from Agent 1!"}
    # )
    
    print("A2A communication example completed")


async def example_mcp_integration():
    """Example of MCP server integration."""
    
    # Create MCP server
    server = MCPServer("document_server", "1.0")
    
    # Add a resource
    doc_resource = MCPResource(
        uri="documents://company-docs",
        name="Company Documents",
        description="Access to company documentation",
        mime_type="application/json"
    )
    
    async def read_documents(uri: str) -> Dict[str, Any]:
        return {"documents": ["doc1.pdf", "doc2.pdf"]}
    
    server.add_resource(doc_resource, read_documents)
    
    # Add a tool
    search_tool = MCPTool(
        name="search_documents",
        description="Search through documents",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    )
    
    async def search_documents(arguments: Dict[str, Any]) -> Dict[str, Any]:
        query = arguments["query"]
        limit = arguments.get("limit", 10)
        
        # Mock search results
        return {
            "results": [
                {"title": f"Document about {query}", "score": 0.95},
                {"title": f"Related {query} info", "score": 0.87}
            ][:limit]
        }
    
    server.add_tool(search_tool, search_documents)
    
    # Create agent with MCP support
    # agent = ProtocolEnabledAgent(your_agent, mcp_servers=[server])
    
    # Use MCP resources
    # resources = await agent.get_mcp_resources()
    # print(f"Available resources: {[r.name for r in resources]}")
    
    # Use MCP tool
    # search_result = await agent.use_mcp_tool("search_documents", {"query": "AI"})
    # print(f"Search results: {search_result}")
    
    print("MCP integration example completed")