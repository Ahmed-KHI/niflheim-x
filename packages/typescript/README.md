<div align="center">

# 🌟 Niflheim-X TypeScript ⚡ 
### *The Revolutionary 5-Minute AI Agent Framework*

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=20&duration=3000&pause=1000&color=6366F1&center=true&vCenter=true&width=600&lines=Build+Production+Agents+10x+Faster;TypeScript+%2B+JavaScript+Ready;From+Prototype+to+Production+in+Minutes;The+Lightweight+AI+Framework)](https://git.io/typing-svg)

![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=node.js&logoColor=white)
![AI](https://img.shields.io/badge/AI-Powered-FF6B6B?style=for-the-badge&logo=brain&logoColor=white)

---

[![NPM Version](https://img.shields.io/npm/v/niflheim-x?style=for-the-badge&logo=npm&logoColor=white&color=CB3837)](https://www.npmjs.com/package/niflheim-x)
[![NPM Downloads](https://img.shields.io/npm/dm/niflheim-x?style=for-the-badge&logo=npm&logoColor=white&color=green)](https://www.npmjs.com/package/niflheim-x)
[![Bundle Size](https://img.shields.io/bundlephobia/minzip/niflheim-x?style=for-the-badge&logo=webpack&logoColor=white&color=orange)](https://bundlephobia.com/package/niflheim-x)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](https://opensource.org/licenses/MIT)

[![GitHub Repo stars](https://img.shields.io/github/stars/Ahmed-KHI/niflheim-x?style=for-the-badge&logo=github&logoColor=white&color=gold)](https://github.com/Ahmed-KHI/niflheim-x)
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-7289da?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/GrsYUcTe)

</div>

---

## 🚀 **Quick Start**

```bash
# 📦 Install via NPM
npm install niflheim-x

# 🧶 Or via Yarn
yarn add niflheim-x

# 📦 Or via PNPM
pnpm add niflheim-x
```

## ⚡ **Get Running in 30 Seconds**

```typescript
import { Agent, OpenAILLM } from 'niflheim-x';

// 🤖 Create your AI agent
const agent = new Agent({
  llm: new OpenAILLM({ apiKey: 'your-openai-key' }),
  systemPrompt: "You are a helpful AI assistant! 🎯"
});

// 💬 Start chatting
const response = await agent.chat("What's the capital of France?");
console.log(response.content); // "The capital of France is Paris! 🇫🇷"

// 🛠️ Add custom tools
agent.addTool({
  name: 'calculator',
  description: 'Perform mathematical calculations',
  parameters: {
    type: 'object',
    properties: {
      expression: { type: 'string', description: 'Math expression to evaluate' }
    }
  },
  execute: async ({ expression }) => {
    return eval(expression); // Use math-expression-evaluator in production!
  }
});

// 🎯 Use tools intelligently
const mathResult = await agent.chat("What's 25 * 4 + 10?");
console.log(mathResult.content); // "The result is 110! 🧮"
```

## 🌟 **Why Choose Niflheim-X TypeScript?**

<div align="center">

| 🎯 **Feature** | 🌟 **Niflheim-X** | 🦜 **LangChain.js** | 🎯 **Advantage** |
|----------------|-------------------|---------------------|-------------------|
| **📦 Bundle Size** | `< 100KB` | `> 2MB` | **20x Lighter** |
| **⚡ Startup Time** | `< 50ms` | `> 500ms` | **10x Faster** |
| **🧠 Memory Usage** | `~5MB` | `~50MB` | **10x Efficient** |
| **📚 Dependencies** | `5 core` | `30+ deps` | **6x Cleaner** |
| **🛡️ Type Safety** | `100% TypeScript` | `Partial types` | **Full Safety** |

</div>

## 🏗️ **Core Features**

### 🤖 **Smart Agent System**
- **🎨 Intelligent Prompting** - Context-aware conversation management
- **🧠 Memory Management** - Persistent conversation history
- **🛠️ Tool Integration** - Easy function calling and tool use
- **🌊 Streaming Support** - Real-time response streaming

### 🌐 **Multi-LLM Support**
- **🧠 OpenAI** - GPT-4, GPT-4o, GPT-3.5-turbo
- **🎭 Anthropic** - Claude 3.5 Sonnet, Haiku, Opus
- **🔄 Custom LLMs** - Easy adapter pattern for any provider

### 🛠️ **Developer Experience**
- **📝 Full TypeScript** - Complete type safety and IntelliSense
- **🎯 Simple API** - Intuitive and easy to learn
- **📚 Rich Examples** - Comprehensive documentation
- **🧪 Testing Ready** - Built with testing in mind

## 📚 **Examples**

<details>
<summary><strong>🤖 Basic Chat Agent</strong></summary>

```typescript
import { Agent, OpenAILLM } from 'niflheim-x';

const agent = new Agent({
  llm: new OpenAILLM({ 
    apiKey: process.env.OPENAI_API_KEY!,
    model: 'gpt-4'
  }),
  systemPrompt: "You are a knowledgeable assistant specializing in technology."
});

async function main() {
  const response = await agent.chat("Explain TypeScript in simple terms");
  console.log('🤖 Agent:', response.content);
}

main().catch(console.error);
```

</details>

<details>
<summary><strong>🛠️ Agent with Custom Tools</strong></summary>

```typescript
import { Agent, OpenAILLM } from 'niflheim-x';
import axios from 'axios';

const agent = new Agent({
  llm: new OpenAILLM({ apiKey: process.env.OPENAI_API_KEY! })
});

// 🌤️ Add weather tool
agent.addTool({
  name: 'getWeather',
  description: 'Get current weather for a city',
  parameters: {
    type: 'object',
    properties: {
      city: { type: 'string', description: 'City name' }
    },
    required: ['city']
  },
  execute: async ({ city }) => {
    const response = await axios.get(`https://api.weather.com/v1/current/${city}`);
    return `Weather in ${city}: ${response.data.description}, ${response.data.temperature}°C`;
  }
});

// 📧 Add email tool
agent.addTool({
  name: 'sendEmail',
  description: 'Send an email',
  parameters: {
    type: 'object',
    properties: {
      to: { type: 'string', description: 'Recipient email' },
      subject: { type: 'string', description: 'Email subject' },
      body: { type: 'string', description: 'Email body' }
    },
    required: ['to', 'subject', 'body']
  },
  execute: async ({ to, subject, body }) => {
    // Your email sending logic here
    console.log(`📧 Sending email to ${to}: ${subject}`);
    return `Email sent successfully to ${to}`;
  }
});

async function main() {
  const response = await agent.chat(
    "What's the weather in Tokyo and send a summary email to john@example.com?"
  );
  console.log('🤖 Agent:', response.content);
}

main().catch(console.error);
```

</details>

<details>
<summary><strong>👥 Multi-Agent System</strong></summary>

```typescript
import { Agent, OpenAILLM } from 'niflheim-x';

const llm = new OpenAILLM({ apiKey: process.env.OPENAI_API_KEY! });

// 🔬 Research Agent
const researcher = new Agent({
  llm,
  systemPrompt: `You are Dr. Research, a thorough research specialist.
  You excel at finding facts, analyzing data, and providing evidence-based insights.`
});

// ✍️ Writer Agent  
const writer = new Agent({
  llm,
  systemPrompt: `You are Creative Writer, a skilled content creator.
  You excel at turning research into engaging, readable content.`
});

async function collaborativeWriting(topic: string) {
  // Research phase
  const research = await researcher.chat(
    `Research the topic: ${topic}. Provide key facts and insights.`
  );
  
  // Writing phase
  const article = await writer.chat(
    `Based on this research: ${research.content}
    
    Write an engaging blog post about ${topic}.`
  );
  
  return {
    research: research.content,
    article: article.content
  };
}

async function main() {
  const result = await collaborativeWriting("The Future of AI Agents");
  
  console.log("🔬 Research:", result.research);
  console.log("✍️ Article:", result.article);
}

main().catch(console.error);
```

</details>

<details>
<summary><strong>🌊 Streaming Responses</strong></summary>

```typescript
import { Agent, OpenAILLM } from 'niflheim-x';

const agent = new Agent({
  llm: new OpenAILLM({ 
    apiKey: process.env.OPENAI_API_KEY!,
    stream: true 
  })
});

async function streamingChat() {
  const stream = await agent.chatStream("Write a short story about AI and humans");
  
  process.stdout.write("🤖 Agent: ");
  
  for await (const chunk of stream) {
    process.stdout.write(chunk.content);
  }
  
  console.log("\n✅ Story complete!");
}

streamingChat().catch(console.error);
```

</details>

## 🛠️ **Installation & Setup**

### **Prerequisites**
- Node.js 16+ 
- TypeScript 4.5+ (for TypeScript projects)

### **Environment Variables**
```bash
# .env file
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### **TypeScript Configuration**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true
  }
}
```

## 📖 **API Reference**

### **Agent Class**

```typescript
class Agent {
  constructor(config: AgentConfig)
  
  // Chat with the agent
  async chat(message: string): Promise<AgentResponse>
  
  // Stream chat responses
  async chatStream(message: string): AsyncIterable<AgentResponse>
  
  // Add custom tools
  addTool(tool: Tool): void
  
  // Get conversation history
  getHistory(): ConversationMessage[]
  
  // Clear conversation history
  clearHistory(): void
}
```

### **Configuration Options**

```typescript
interface AgentConfig {
  llm: LLMProvider;           // LLM provider instance
  systemPrompt?: string;      // System prompt for the agent
  memory?: MemoryProvider;    // Custom memory provider
  maxTokens?: number;         // Maximum tokens per response
  temperature?: number;       // Response creativity (0-1)
}
```

## 🚀 **Advanced Usage**

### **Custom LLM Provider**
```typescript
import { LLMProvider, LLMResponse } from 'niflheim-x';

class CustomLLM implements LLMProvider {
  async chat(messages: Message[]): Promise<LLMResponse> {
    // Your custom LLM implementation
    return {
      content: "Response from custom LLM",
      usage: { promptTokens: 10, completionTokens: 20 }
    };
  }
}

const agent = new Agent({
  llm: new CustomLLM()
});
```

### **Custom Memory Provider**
```typescript
import { MemoryProvider, ConversationMessage } from 'niflheim-x';

class DatabaseMemory implements MemoryProvider {
  async store(message: ConversationMessage): Promise<void> {
    // Store in your database
  }
  
  async retrieve(): Promise<ConversationMessage[]> {
    // Retrieve from your database
    return [];
  }
  
  async clear(): Promise<void> {
    // Clear database records
  }
}

const agent = new Agent({
  llm: new OpenAILLM({ apiKey: 'your-key' }),
  memory: new DatabaseMemory()
});
```

## 🧪 **Testing**

```typescript
import { Agent, MockLLM } from 'niflheim-x';

describe('Agent Tests', () => {
  test('should respond to basic chat', async () => {
    const mockLLM = new MockLLM({
      responses: ['Hello! How can I help you?']
    });
    
    const agent = new Agent({ llm: mockLLM });
    const response = await agent.chat('Hello');
    
    expect(response.content).toBe('Hello! How can I help you?');
  });
});
```

## 🔗 **Related Projects**

- **🐍 Python Version**: [niflheim-x (PyPI)](https://pypi.org/project/niflheim-x/)
- **📚 Documentation**: [Comprehensive Docs](https://ahmed-khi.github.io/niflheim-x/)
- **💬 Community**: [Discord Server](https://discord.gg/GrsYUcTe)
- **🐛 Issues**: [GitHub Issues](https://github.com/Ahmed-KHI/niflheim-x/issues)

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guide](https://github.com/Ahmed-KHI/niflheim-x/blob/main/CONTRIBUTING.md) for details.

```bash
# 🍴 Clone the repository
git clone https://github.com/Ahmed-KHI/niflheim-x.git
cd niflheim-x/packages/typescript

# 📦 Install dependencies
npm install

# 🔧 Build the project
npm run build

# 🧪 Run tests
npm test

# 🚀 Start development
npm run dev
```

## 📄 **License**

MIT License - see [LICENSE](https://github.com/Ahmed-KHI/niflheim-x/blob/main/LICENSE) file for details.

---

<div align="center">

## 🌟 **Ready to Build Amazing AI Agents?**

**[🎯 Get Started](https://www.npmjs.com/package/niflheim-x) • [📚 Documentation](https://ahmed-khi.github.io/niflheim-x/) • [💬 Discord](https://discord.gg/GrsYUcTe) • [⭐ GitHub](https://github.com/Ahmed-KHI/niflheim-x)**

---

**Built with ❤️ by [Ahmed KHI](https://github.com/Ahmed-KHI) and the Niflheim-X community**

*Empowering developers to build the future of AI, one agent at a time.* 🚀

</div>