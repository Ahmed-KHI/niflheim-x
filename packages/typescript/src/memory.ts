/**
 * Memory backends for TypeScript implementation
 */

import { Message, MessageList } from './types.js';

export abstract class MemoryBackend {
  abstract addMessage(sessionId: string, message: Message): Promise<void>;
  abstract getMessages(sessionId: string, limit?: number): Promise<MessageList>;
  abstract clearSession(sessionId: string): Promise<void>;
  abstract getSessionCount(sessionId: string): Promise<number>;
}

export class DictMemory extends MemoryBackend {
  private sessions: Map<string, Message[]> = new Map();
  private maxMessages: number;

  constructor(maxMessages: number = 1000) {
    super();
    this.maxMessages = maxMessages;
  }

  async addMessage(sessionId: string, message: Message): Promise<void> {
    if (!this.sessions.has(sessionId)) {
      this.sessions.set(sessionId, []);
    }

    const messages = this.sessions.get(sessionId)!;
    messages.push(message);

    // Trim old messages if we exceed max
    if (messages.length > this.maxMessages) {
      this.sessions.set(sessionId, messages.slice(-this.maxMessages));
    }
  }

  async getMessages(sessionId: string, limit?: number): Promise<MessageList> {
    const messages = this.sessions.get(sessionId) || [];
    
    if (limit !== undefined) {
      return messages.slice(-limit);
    }
    
    return [...messages];
  }

  async clearSession(sessionId: string): Promise<void> {
    this.sessions.delete(sessionId);
  }

  async getSessionCount(sessionId: string): Promise<number> {
    return this.sessions.get(sessionId)?.length || 0;
  }
}

export class SQLiteMemory extends MemoryBackend {
  private dbPath: string;
  private maxMessages: number;

  constructor(dbPath: string = 'memory.db', maxMessages: number = 10000) {
    super();
    this.dbPath = dbPath;
    this.maxMessages = maxMessages;
    // In a real implementation, you'd use better-sqlite3 or similar
    throw new Error('SQLite memory backend not yet implemented for TypeScript');
  }

  async addMessage(sessionId: string, message: Message): Promise<void> {
    throw new Error('Not implemented');
  }

  async getMessages(sessionId: string, limit?: number): Promise<MessageList> {
    throw new Error('Not implemented');
  }

  async clearSession(sessionId: string): Promise<void> {
    throw new Error('Not implemented');
  }

  async getSessionCount(sessionId: string): Promise<number> {
    throw new Error('Not implemented');
  }
}

export function createMemoryBackend(backendType: string): MemoryBackend {
  switch (backendType) {
    case 'memory':
    case 'dict':
      return new DictMemory();
    case 'sqlite':
      return new SQLiteMemory();
    default:
      throw new Error(`Unsupported backend type: ${backendType}`);
  }
}