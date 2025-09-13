# Niflheim-X TypeScript Framework

🚀 **Enterprise AI Agent Framework - TypeScript Edition**

A powerful, type-safe TypeScript implementation of the Niflheim-X AI agent framework, providing the same enterprise capabilities as our Python version with full TypeScript support.

## ✨ Features

- **🔒 Type Safety**: Full TypeScript support with comprehensive type definitions
- **⚡ Async-First**: Built for modern async/await patterns and streaming
- **🧠 Memory Systems**: Multiple memory backends (Dict, SQLite, Vector)
- **🛠️ Tool Integration**: Easy tool registration and execution
- **🤖 Multi-LLM Support**: OpenAI, Anthropic, and custom LLM adapters
- **📊 Enterprise Ready**: Observability, monitoring, and multi-agent workflows
- **🎯 Lightweight**: Minimal dependencies, maximum performance

## 🚀 Quick Start

### Installation

```bash
npm install @niflheim-x/typescript
```

### Basic Usage

```typescript
import { Agent, SimpleDictMemory, ToolRegistry, createTool, OpenAILLM } from '@niflheim-x/typescript';

// Create memory and tools
const memory = new SimpleDictMemory();
const toolRegistry = new ToolRegistry();

// Add a simple tool
const weatherTool = createTool({
  name: 'get_weather',
  description: 'Get weather for a location',
  function: (location: string) => {
    return `The weather in ${location} is sunny and 72°F`;
  },
  parameters: {
    type: 'object',
    properties: {
      location: { type: 'string', description: 'Location to get weather for' }
    },
    required: ['location']
  }
});

toolRegistry.registerTool(weatherTool);

// Create LLM and agent
const llm = new OpenAILLM({
  model: 'gpt-3.5-turbo',
  apiKey: 'your-api-key-here'
});

const agent = new Agent({
  name: 'WeatherBot',
  llm,
  memory,
  toolRegistry,
  systemPrompt: 'You are a helpful weather assistant.'
});

// Chat with the agent
const response = await agent.chat('What is the weather like in San Francisco?');
console.log(response.content);
```

## 🏗️ Architecture

### Core Components

- **Agent**: Main orchestrator for conversations and tool execution
- **Memory**: Pluggable storage backends for conversation history
- **Tools**: Function calling system with automatic parameter validation
- **LLM Adapters**: Unified interface for different language models

### Memory Backends

```typescript
// Simple in-memory storage
const dictMemory = new SimpleDictMemory();

// Persistent SQLite storage
const sqliteMemory = new SQLiteMemory('./conversations.db');

// Vector database integration
const vectorMemory = new VectorMemory({ 
  provider: 'pinecone',
  apiKey: 'your-key'
});
```

### Tool System

```typescript
const calculatorTool = createTool({
  name: 'calculate',
  description: 'Perform mathematical calculations',
  function: (expression: string) => {
    return eval(expression); // Note: Use a safe eval in production
  },
  parameters: {
    type: 'object',
    properties: {
      expression: { type: 'string', description: 'Mathematical expression' }
    },
    required: ['expression']
  },
  timeout: 5.0 // 5 second timeout
});

agent.registerTool(calculatorTool);
```

### Streaming Support

```typescript
for await (const chunk of agent.stream('Tell me a long story')) {
  if (chunk.content) {
    process.stdout.write(chunk.content);
  }
  
  if (chunk.finished) {
    console.log('\\n\\nStory complete!');
    break;
  }
}
```

## 🔧 Configuration

### Agent Configuration

```typescript
const agent = new Agent({
  name: 'MyAgent',
  llm: new OpenAILLM({ model: 'gpt-4', apiKey: 'key' }),
  memory: new SimpleDictMemory(),
  toolRegistry: new ToolRegistry(),
  systemPrompt: 'You are a helpful assistant.',
  maxMemoryMessages: 100,
  enableStreaming: true
});
```

### LLM Configuration

```typescript
// OpenAI
const openaiLLM = new OpenAILLM({
  model: 'gpt-4-turbo',
  apiKey: 'your-key',
  temperature: 0.7,
  maxTokens: 2048
});

// Anthropic
const anthropicLLM = new AnthropicLLM({
  model: 'claude-3-sonnet-20240229',
  apiKey: 'your-key',
  temperature: 0.7,
  maxTokens: 4096
});
```

## 📊 Events & Monitoring

The agent emits events for comprehensive monitoring:

```typescript
agent.on('chat:start', (data) => {
  console.log('Chat started:', data.message);
});

agent.on('tool:call', (toolCall) => {
  console.log('Tool called:', toolCall.name);
});

agent.on('llm:response', (response) => {
  console.log('LLM responded with', response.usage?.totalTokens, 'tokens');
});

agent.on('chat:complete', (response) => {
  console.log('Chat completed:', response.content);
});
```

## 🏢 Enterprise Features

### Multi-Agent Workflows

```typescript
import { WorkflowOrchestrator } from '@niflheim-x/typescript';

const orchestrator = new WorkflowOrchestrator();

// Define workflow steps
const workflow = {
  id: 'research-workflow',
  steps: [
    { type: 'agent', agentId: 'researcher', input: 'topic' },
    { type: 'agent', agentId: 'analyst', input: 'research_results' },
    { type: 'agent', agentId: 'writer', input: 'analysis' }
  ]
};

const result = await orchestrator.execute(workflow, { topic: 'AI trends 2024' });
```

### Observability

```typescript
import { MetricsCollector, TracingProvider } from '@niflheim-x/typescript';

const metrics = new MetricsCollector();
const tracer = new TracingProvider('jaeger');

agent.on('chat:complete', (response) => {
  metrics.recordChatCompletion({
    duration: response.metadata.duration,
    tokens: response.usage?.totalTokens,
    agent: response.metadata.agentName
  });
});
```

## 📦 Building & Development

### Build from Source

```bash
git clone https://github.com/niflheim-x/framework.git
cd framework/packages/typescript
npm install
npm run build
```

### Development

```bash
npm run dev    # Watch mode
npm run test   # Run tests
npm run lint   # Lint code
```

## 🆚 Comparison

| Feature | Niflheim-X | LangChain | BeeAI |
|---------|------------|-----------|-------|
| **Size** | 50KB | 10MB+ | 2MB+ |
| **Dependencies** | 3 core | 100+ | 50+ |
| **TypeScript** | ✅ Native | ⚠️ Partial | ✅ Native |
| **Async-First** | ✅ | ⚠️ | ✅ |
| **Enterprise** | ✅ | ❌ | ✅ |
| **Multi-Agent** | ✅ | ❌ | ✅ |

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🔗 Links

- **Python Version**: [@niflheim-x/python](../python)
- **Documentation**: [niflheim-x.dev](https://niflheim-x.dev)
- **GitHub**: [github.com/niflheim-x/framework](https://github.com/niflheim-x/framework)
- **Discord**: [Join our community](https://discord.gg/niflheim-x)

---

**⚡ Ready to build the future of AI agents? Get started with Niflheim-X TypeScript today!**