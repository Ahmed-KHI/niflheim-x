/**
 * Tool system for TypeScript implementation
 */

import { ToolCall, ToolResult } from './types.js';

export interface Tool {
  name: string;
  description: string;
  function: (...args: any[]) => any | Promise<any>;
  parameters: Record<string, any>;
  timeout: number;
}

export class ToolRegistry {
  private tools: Map<string, Tool> = new Map();

  registerTool(tool: Tool): void {
    this.tools.set(tool.name, tool);
  }

  getTool(name: string): Tool | undefined {
    return this.tools.get(name);
  }

  listTools(): Tool[] {
    return Array.from(this.tools.values());
  }

  getOpenAITools(): any[] {
    return Array.from(this.tools.values()).map(tool => ({
      type: 'function',
      function: {
        name: tool.name,
        description: tool.description,
        parameters: tool.parameters
      }
    }));
  }

  getAnthropicTools(): any[] {
    return Array.from(this.tools.values()).map(tool => ({
      name: tool.name,
      description: tool.description,
      input_schema: tool.parameters
    }));
  }

  async executeTool(toolCall: ToolCall): Promise<ToolResult> {
    const startTime = Date.now();
    
    const tool = this.getTool(toolCall.name);
    if (!tool) {
      return {
        callId: toolCall.callId,
        error: `Tool '${toolCall.name}' not found`,
        executionTime: Date.now() - startTime
      };
    }

    try {
      // Execute with timeout
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Tool execution timeout')), tool.timeout * 1000);
      });

      const executionPromise = Promise.resolve(tool.function(toolCall.arguments));
      
      const result = await Promise.race([executionPromise, timeoutPromise]);

      return {
        callId: toolCall.callId,
        result,
        executionTime: Date.now() - startTime
      };
    } catch (error) {
      return {
        callId: toolCall.callId,
        error: error instanceof Error ? error.message : String(error),
        executionTime: Date.now() - startTime
      };
    }
  }
}

// Helper function to create a tool
export function createTool(config: {
  name: string;
  description: string;
  function: (...args: any[]) => any | Promise<any>;
  parameters?: Record<string, any>;
  timeout?: number;
}): Tool {
  return {
    name: config.name,
    description: config.description,
    function: config.function,
    parameters: config.parameters || {
      type: 'object',
      properties: {},
      required: []
    },
    timeout: config.timeout || 30.0
  };
}