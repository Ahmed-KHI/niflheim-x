/**
 * Simple Agent implementation for TypeScript
 */

import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import { 
  Message, 
  MessageRole,
  ToolCall, 
  ToolResult, 
  AgentResponse 
} from './types.js';
import { MemoryBackend } from './memory.js';
import { ToolRegistry } from './tools.js';
import { BaseLLM, LLMResponse, StreamChunk } from './llm/base.js';

// Simple memory interface for our agent
export interface SimpleMemory {
  addMessage(message: Message): Promise<void>;
  getMessages(): Message[];
  clear(): Promise<void>;
}

export class SimpleDictMemory implements SimpleMemory {
  private messages: Message[] = [];
  private maxMessages: number;

  constructor(maxMessages: number = 1000) {
    this.maxMessages = maxMessages;
  }

  async addMessage(message: Message): Promise<void> {
    this.messages.push(message);
    
    // Keep only recent messages
    if (this.messages.length > this.maxMessages) {
      this.messages = this.messages.slice(-this.maxMessages);
    }
  }

  getMessages(): Message[] {
    return [...this.messages];
  }

  async clear(): Promise<void> {
    this.messages = [];
  }
}

export interface SimpleAgentConfig {
  name?: string;
  llm: BaseLLM;
  memory?: SimpleMemory;
  toolRegistry?: ToolRegistry;
  systemPrompt?: string;
  maxMemoryMessages?: number;
  enableStreaming?: boolean;
}

/**
 * TypeScript Agent class for conversational AI
 */
export class Agent extends EventEmitter {
  private id: string;
  private name: string;
  private llm: BaseLLM;
  private memory: SimpleMemory;
  private toolRegistry: ToolRegistry;
  private systemPrompt: string;
  private maxMemoryMessages: number;
  private enableStreaming: boolean;

  constructor(config: SimpleAgentConfig) {
    super();
    
    this.id = uuidv4();
    this.name = config.name || 'NiflheimAgent';
    this.llm = config.llm;
    this.memory = config.memory || new SimpleDictMemory();
    this.toolRegistry = config.toolRegistry || new ToolRegistry();
    this.systemPrompt = config.systemPrompt || 'You are a helpful AI assistant.';
    this.maxMemoryMessages = config.maxMemoryMessages || 50;
    this.enableStreaming = config.enableStreaming || false;
    
    this.emit('agent:created', { id: this.id, name: this.name });
  }

  /**
   * Get agent metadata
   */
  getInfo(): { id: string; name: string; messageCount: number } {
    return {
      id: this.id,
      name: this.name,
      messageCount: this.memory.getMessages().length
    };
  }

  /**
   * Add a message to memory
   */
  async addMessage(message: Message): Promise<void> {
    await this.memory.addMessage(message);
    this.emit('message:added', message);
  }

  /**
   * Get conversation history
   */
  getMessages(): Message[] {
    const messages = this.memory.getMessages();
    if (messages.length > this.maxMemoryMessages) {
      // Keep system message and recent messages
      const systemMessages = messages.filter((m: Message) => m.role === MessageRole.System);
      const otherMessages = messages.filter((m: Message) => m.role !== MessageRole.System);
      const recentMessages = otherMessages.slice(-this.maxMemoryMessages + systemMessages.length);
      return [...systemMessages, ...recentMessages];
    }
    return messages;
  }

  /**
   * Convert LLM tool calls to our ToolCall format
   */
  private convertToolCalls(llmToolCalls: Array<{
    id: string;
    type: string;
    function: {
      name: string;
      arguments: string;
    };
  }>): ToolCall[] {
    return llmToolCalls.map(tc => ({
      name: tc.function.name,
      arguments: JSON.parse(tc.function.arguments),
      callId: tc.id
    }));
  }

  /**
   * Process tool calls from LLM response
   */
  private async executeToolCalls(toolCalls: ToolCall[]): Promise<ToolResult[]> {
    const results: ToolResult[] = [];
    
    for (const toolCall of toolCalls) {
      this.emit('tool:call', toolCall);
      const result = await this.toolRegistry.executeTool(toolCall);
      results.push(result);
      this.emit('tool:result', result);
    }
    
    return results;
  }

  /**
   * Main chat method
   */
  async chat(userMessage: string): Promise<AgentResponse> {
    this.emit('chat:start', { message: userMessage });

    // Add user message to memory
    const userMsg: Message = {
      role: MessageRole.User,
      content: userMessage,
      timestamp: new Date()
    };
    await this.addMessage(userMsg);

    // Prepare messages for LLM
    const messages = this.getMessages();
    
    // Add system prompt if not present
    if (!messages.some(m => m.role === MessageRole.System)) {
      messages.unshift({
        role: MessageRole.System,
        content: this.systemPrompt,
        timestamp: new Date()
      });
    }

    // Get available tools
    const tools = this.toolRegistry.getOpenAITools();

    try {
      // Call LLM
      this.emit('llm:request', { messages, tools });
      const response = await this.llm.chat(messages, tools.length > 0 ? tools : undefined);
      this.emit('llm:response', response);

      let finalContent = response.content;
      const allToolCalls: ToolCall[] = [];

      // Handle tool calls if present
      if (response.toolCalls && response.toolCalls.length > 0) {
        const convertedToolCalls = this.convertToolCalls(response.toolCalls);
        const toolResults = await this.executeToolCalls(convertedToolCalls);
        allToolCalls.push(...convertedToolCalls);

        // Add assistant message with tool calls
        await this.addMessage({
          role: MessageRole.Assistant,
          content: response.content,
          toolCalls: convertedToolCalls,
          timestamp: new Date()
        });

        // Add tool results as messages
        for (const result of toolResults) {
          await this.addMessage({
            role: MessageRole.Tool,
            content: result.error || JSON.stringify(result.result),
            toolCallId: result.callId,
            timestamp: new Date()
          });
        }

        // Get follow-up response with tool results
        const updatedMessages = this.getMessages();
        const followupResponse = await this.llm.chat(updatedMessages);
        finalContent = followupResponse.content;
        
        if (followupResponse.toolCalls) {
          const followupConverted = this.convertToolCalls(followupResponse.toolCalls);
          allToolCalls.push(...followupConverted);
        }
      }

      // Add final assistant message
      const assistantMsg: Message = {
        role: MessageRole.Assistant,
        content: finalContent,
        timestamp: new Date()
      };
      await this.addMessage(assistantMsg);

      const agentResponse: AgentResponse = {
        content: finalContent,
        toolCalls: allToolCalls,
        metadata: {
          agentId: this.id,
          agentName: this.name,
          messageCount: this.memory.getMessages().length
        },
        usage: response.usage ? {
          promptTokens: response.usage.promptTokens || 0,
          completionTokens: response.usage.completionTokens || 0,
          totalTokens: response.usage.totalTokens || 0
        } : undefined,
        finishReason: 'stop'
      };

      this.emit('chat:complete', agentResponse);
      return agentResponse;

    } catch (error) {
      this.emit('chat:error', error);
      throw error;
    }
  }

  /**
   * Streaming chat method
   */
  async *stream(userMessage: string): AsyncIterableIterator<StreamChunk> {
    this.emit('stream:start', { message: userMessage });

    // Add user message to memory
    const userMsg: Message = {
      role: MessageRole.User,
      content: userMessage,
      timestamp: new Date()
    };
    await this.addMessage(userMsg);

    // Prepare messages for LLM
    const messages = this.getMessages();
    
    // Add system prompt if not present
    if (!messages.some(m => m.role === MessageRole.System)) {
      messages.unshift({
        role: MessageRole.System,
        content: this.systemPrompt,
        timestamp: new Date()
      });
    }

    // Get available tools
    const tools = this.toolRegistry.getOpenAITools();

    try {
      let fullContent = '';
      
      // Stream from LLM
      for await (const chunk of this.llm.stream(messages, tools.length > 0 ? tools : undefined)) {
        if (chunk.content) {
          fullContent += chunk.content;
        }
        
        this.emit('stream:chunk', chunk);
        yield chunk;
        
        if (chunk.finished) {
          break;
        }
      }

      // Add assistant message to memory
      if (fullContent) {
        await this.addMessage({
          role: MessageRole.Assistant,
          content: fullContent,
          timestamp: new Date()
        });
      }

      this.emit('stream:complete');

    } catch (error) {
      this.emit('stream:error', error);
      throw error;
    }
  }

  /**
   * Register a tool with the agent
   */
  registerTool(tool: any): void {
    this.toolRegistry.registerTool(tool);
    this.emit('tool:registered', { name: tool.name });
  }

  /**
   * Clear conversation history
   */
  async clearHistory(): Promise<void> {
    await this.memory.clear();
    this.emit('history:cleared');
  }

  /**
   * Get session ID for this agent instance
   */
  getSessionId(): string {
    return this.id;
  }
}