/**
 * Core type definitions for Niflheim-X TypeScript
 */

export enum MessageRole {
  System = 'system',
  User = 'user',
  Assistant = 'assistant',
  Tool = 'tool'
}

export interface Message {
  role: MessageRole;
  content: string;
  metadata?: Record<string, any>;
  timestamp: Date;
  agentName?: string;
  toolCalls?: ToolCall[];
  toolCallId?: string;
}

export interface ToolCall {
  name: string;
  arguments: Record<string, any>;
  callId: string;
}

export interface ToolResult {
  callId: string;
  result?: any;
  error?: string;
  executionTime: number;
}

export interface AgentResponse {
  content: string;
  toolCalls: ToolCall[];
  metadata: Record<string, any>;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  finishReason: string;
}

export interface StreamingToken {
  content: string;
  isToolCall: boolean;
  finishReason?: string;
}

export interface LLMConfig {
  model: string;
  temperature: number;
  maxTokens?: number;
  topP: number;
  frequencyPenalty: number;
  presencePenalty: number;
  stream: boolean;
}

export interface AgentConfig {
  name: string;
  systemPrompt: string;
  memoryBackend: 'memory' | 'sqlite' | 'vector';
  maxMemoryMessages: number;
  toolTimeout: number;
  enableStreaming: boolean;
}

export interface ObservabilityConfig {
  enableMetrics: boolean;
  enableTracing: boolean;
  enableLogging: boolean;
  metricsProvider?: 'prometheus' | 'datadog' | 'custom';
  tracingProvider?: 'jaeger' | 'zipkin' | 'custom';
}

export interface WorkflowStep {
  id: string;
  type: 'agent' | 'tool' | 'condition' | 'parallel';
  config: Record<string, any>;
  nextSteps: string[];
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  entryPoint: string;
}

// Enterprise features
export interface TenantConfig {
  id: string;
  name: string;
  settings: Record<string, any>;
  limits: {
    maxAgents: number;
    maxTokensPerMonth: number;
    maxConcurrentRequests: number;
  };
}

export interface UserRole {
  id: string;
  name: string;
  permissions: string[];
}

export type MessageList = Message[];
export type ToolCallList = ToolCall[];
export type ToolResultList = ToolResult[];