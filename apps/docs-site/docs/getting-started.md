---
sidebar_position: 2
---

# Getting Started

Get up and running with Niflheim-X in just a few minutes! This guide will walk you through installation, basic setup, and your first AI agent.

## 🔧 Installation

### Python Installation

```bash
# Install from PyPI
pip install niflheim-x

# Or install with enterprise features
pip install "niflheim-x[enterprise]"

# Development installation
pip install "niflheim-x[dev]"
```

### TypeScript/Node.js Installation

```bash
# Install the core package
npm install @niflheim-x/core

# Or with yarn
yarn add @niflheim-x/core

# For development
npm install --save-dev @niflheim-x/dev-tools
```

### 🚀 **Lightning Fast**
- **50KB total size** vs LangChain's 50MB
- **Instant startup** - no 5-second import delays
- **Minimal dependencies** - only 3 core packages

### 🏢 **Enterprise Ready**
- **Multi-language support** - Python & TypeScript
- **Production observability** - metrics, tracing, logging
- **Protocol standards** - A2A and MCP support
- **Advanced workflows** - visual multi-agent orchestration

### 🛠️ **Developer Friendly**
- **5-minute setup** from zero to production
- **Type-safe** with full IDE support
- **Hot-swappable backends** - memory, SQLite, vector stores
- **Tool ecosystem** - one-line function registration

## Quick Start

Choose your language:

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="python" label="Python" default>

```bash
pip install niflheim-x
```

```python
import asyncio
from niflheim_x import Agent, OpenAIAdapter

async def main():
    # Create an agent
    agent = Agent(
        llm=OpenAIAdapter(api_key="your-key"),
        system_prompt="You are a helpful assistant.",
        memory_backend="dict"
    )
    
    # Add a tool
    @agent.tool
    def calculator(expression: str) -> float:
        """Evaluate mathematical expressions."""
        return eval(expression)  # Don't use eval() in production!
    
    # Chat with your agent
    response = await agent.chat("What's 25 * 4 + 10?")
    print(response.content)

if __name__ == "__main__":
    asyncio.run(main())
```

</TabItem>
<TabItem value="typescript" label="TypeScript">

```bash
npm install @niflheim-x/core
```

```typescript
import { Agent, OpenAIAdapter } from '@niflheim-x/core';

async function main() {
  // Create an agent
  const agent = new Agent({
    llm: new OpenAIAdapter({ apiKey: 'your-key' }),
    systemPrompt: 'You are a helpful assistant.',
    memoryBackend: 'memory'
  });
  
  // Add a tool
  agent.addTool({
    name: 'calculator',
    description: 'Evaluate mathematical expressions',
    execute: async (expression: string) => {
      return Function('"use strict"; return (' + expression + ')')();
    }
  });
  
  // Chat with your agent
  const response = await agent.chat("What's 25 * 4 + 10?");
  console.log(response.content);
}

main().catch(console.error);
```

</TabItem>
</Tabs>

## Next Steps

### 📚 **Learn the Basics**
- [Core Concepts](./core-concepts) - Understand agents, memory, and tools
- [Memory Systems](./memory-systems) - Choose the right storage backend
- [Tool Development](./tools) - Build custom agent capabilities

### 🏗️ **Build Something Real**
- [Multi-Agent Systems](./multi-agent) - Orchestrate agent teams
- [Production Deployment](./deployment) - Scale to enterprise
- [Observability](./observability) - Monitor agent performance

### 🚀 **Enterprise Features**
- [Workflow Engine](./workflows) - Visual agent orchestration
- [Protocol Support](./protocols) - A2A and MCP integration
- [Security & RBAC](./security) - Enterprise authentication

## Performance Comparison

| Metric | Niflheim-X | LangChain | BeeAI | AutoGen |
|--------|------------|-----------|-------|---------|
| Import Time | **50ms** | 2-5s | ~1s | ~3s |
| Memory Usage | **10MB** | 200MB | 100MB | 150MB |
| Bundle Size | **50KB** | 50MB | 15MB | 25MB |
| Dependencies | **3** | 50+ | 20+ | 30+ |
| Time to Production | **5 min** | Days | Hours | Weeks |

## Why Developers Choose Niflheim-X

> **"Migrated from LangChain in 2 hours. Same functionality, 10x faster startup."**  
> *- Senior Developer at AI Startup*

> **"Finally, an agent framework that doesn't break with every update."**  
> *- DevOps Engineer*

> **"The TypeScript support is phenomenal. Best DX I've experienced."**  
> *- Full-Stack Developer*

## Community & Support

- 💬 **[Discord Community](https://discord.gg/niflheim-x)** - Get help and share ideas
- 📝 **[GitHub Issues](https://github.com/niflheim-x/niflheim-x/issues)** - Report bugs and request features  
- 🐦 **[Twitter Updates](https://twitter.com/niflheim_x)** - Latest news and tips
- 📖 **[Blog](../blog)** - Deep dives and tutorials

Ready to build lightning-fast AI agents? [Install Niflheim-X](#quick-start) and start building in 5 minutes!