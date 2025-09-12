/**
 * LLM base classes and adapters for TypeScript implementation
 */

import { Message, AgentConfig } from '../types.js';

export interface LLMResponse {
  content: string;
  usage?: {
    promptTokens?: number;
    completionTokens?: number;
    totalTokens?: number;
  };
  toolCalls?: Array<{
    id: string;
    type: string;
    function: {
      name: string;
      arguments: string;
    };
  }>;
}

export interface StreamChunk {
  content?: string;
  delta?: string;
  finished?: boolean;
  toolCalls?: Array<{
    id: string;
    type: string;
    function: {
      name: string;
      arguments: string;
    };
  }>;
}

export abstract class BaseLLM {
  protected model: string;
  protected apiKey: string;
  protected baseURL?: string;
  protected temperature: number;
  protected maxTokens?: number;

  constructor(config: {
    model: string;
    apiKey: string;
    baseURL?: string;
    temperature?: number;
    maxTokens?: number;
  }) {
    this.model = config.model;
    this.apiKey = config.apiKey;
    this.baseURL = config.baseURL;
    this.temperature = config.temperature || 0.7;
    this.maxTokens = config.maxTokens;
  }

  abstract chat(messages: Message[], tools?: any[]): Promise<LLMResponse>;
  abstract stream(messages: Message[], tools?: any[]): AsyncIterableIterator<StreamChunk>;

  protected validateMessages(messages: Message[]): void {
    if (!messages || messages.length === 0) {
      throw new Error('Messages cannot be empty');
    }

    for (const message of messages) {
      if (!message.role || !message.content) {
        throw new Error('Each message must have role and content');
      }
    }
  }
}

export class OpenAILLM extends BaseLLM {
  private async makeRequest(endpoint: string, data: any): Promise<any> {
    const url = `${this.baseURL || 'https://api.openai.com/v1'}/${endpoint}`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`OpenAI API error: ${response.status} - ${error}`);
    }

    return response.json();
  }

  async chat(messages: Message[], tools?: any[]): Promise<LLMResponse> {
    this.validateMessages(messages);

    const data: any = {
      model: this.model,
      messages: messages.map(msg => ({
        role: msg.role,
        content: msg.content
      })),
      temperature: this.temperature
    };

    if (this.maxTokens) {
      data.max_tokens = this.maxTokens;
    }

    if (tools && tools.length > 0) {
      data.tools = tools;
      data.tool_choice = 'auto';
    }

    const response = await this.makeRequest('chat/completions', data);

    return {
      content: response.choices[0]?.message?.content || '',
      usage: response.usage ? {
        promptTokens: response.usage.prompt_tokens,
        completionTokens: response.usage.completion_tokens,
        totalTokens: response.usage.total_tokens
      } : undefined,
      toolCalls: response.choices[0]?.message?.tool_calls
    };
  }

  async *stream(messages: Message[], tools?: any[]): AsyncIterableIterator<StreamChunk> {
    this.validateMessages(messages);

    const data: any = {
      model: this.model,
      messages: messages.map(msg => ({
        role: msg.role,
        content: msg.content
      })),
      temperature: this.temperature,
      stream: true
    };

    if (this.maxTokens) {
      data.max_tokens = this.maxTokens;
    }

    if (tools && tools.length > 0) {
      data.tools = tools;
      data.tool_choice = 'auto';
    }

    const url = `${this.baseURL || 'https://api.openai.com/v1'}/chat/completions`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`OpenAI API error: ${response.status} - ${error}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Failed to get response reader');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed === '' || trimmed === 'data: [DONE]') continue;
          
          if (trimmed.startsWith('data: ')) {
            try {
              const data = JSON.parse(trimmed.slice(6));
              const choice = data.choices?.[0];
              
              if (choice?.delta?.content) {
                yield { content: choice.delta.content };
              }
              
              if (choice?.delta?.tool_calls) {
                yield { toolCalls: choice.delta.tool_calls };
              }
              
              if (choice?.finish_reason) {
                yield { finished: true };
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }
}

export class AnthropicLLM extends BaseLLM {
  private async makeRequest(data: any): Promise<any> {
    const url = `${this.baseURL || 'https://api.anthropic.com'}/v1/messages`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Anthropic API error: ${response.status} - ${error}`);
    }

    return response.json();
  }

  async chat(messages: Message[], tools?: any[]): Promise<LLMResponse> {
    this.validateMessages(messages);

    // Convert messages to Anthropic format
    const anthropicMessages = [];
    let systemMessage = '';

    for (const msg of messages) {
      if (msg.role === 'system') {
        systemMessage = msg.content;
      } else {
        anthropicMessages.push({
          role: msg.role === 'assistant' ? 'assistant' : 'user',
          content: msg.content
        });
      }
    }

    const data: any = {
      model: this.model,
      messages: anthropicMessages,
      max_tokens: this.maxTokens || 4096,
      temperature: this.temperature
    };

    if (systemMessage) {
      data.system = systemMessage;
    }

    if (tools && tools.length > 0) {
      data.tools = tools;
    }

    const response = await this.makeRequest(data);

    return {
      content: response.content?.[0]?.text || '',
      usage: response.usage ? {
        promptTokens: response.usage.input_tokens,
        completionTokens: response.usage.output_tokens,
        totalTokens: response.usage.input_tokens + response.usage.output_tokens
      } : undefined,
      toolCalls: response.content?.filter((c: any) => c.type === 'tool_use')
    };
  }

  async *stream(messages: Message[], tools?: any[]): AsyncIterableIterator<StreamChunk> {
    this.validateMessages(messages);

    // Convert messages to Anthropic format
    const anthropicMessages = [];
    let systemMessage = '';

    for (const msg of messages) {
      if (msg.role === 'system') {
        systemMessage = msg.content;
      } else {
        anthropicMessages.push({
          role: msg.role === 'assistant' ? 'assistant' : 'user',
          content: msg.content
        });
      }
    }

    const data: any = {
      model: this.model,
      messages: anthropicMessages,
      max_tokens: this.maxTokens || 4096,
      temperature: this.temperature,
      stream: true
    };

    if (systemMessage) {
      data.system = systemMessage;
    }

    if (tools && tools.length > 0) {
      data.tools = tools;
    }

    const url = `${this.baseURL || 'https://api.anthropic.com'}/v1/messages`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Anthropic API error: ${response.status} - ${error}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Failed to get response reader');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed === '' || !trimmed.startsWith('data: ')) continue;
          
          try {
            const data = JSON.parse(trimmed.slice(6));
            
            if (data.type === 'content_block_delta' && data.delta?.text) {
              yield { content: data.delta.text };
            }
            
            if (data.type === 'message_stop') {
              yield { finished: true };
            }
          } catch (e) {
            // Skip invalid JSON
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }
}