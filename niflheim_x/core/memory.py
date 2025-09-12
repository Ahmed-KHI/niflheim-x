"""
Memory backends for storing conversation history and context.

This module provides different storage backends for agent memory, from simple
in-memory dictionaries to persistent SQLite databases.
"""

import json
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .types import Message, MessageList


class MemoryBackend(ABC):
    """Abstract base class for memory backends.
    
    Memory backends store and retrieve conversation history for agents.
    They can be implemented using various storage mechanisms like dictionaries,
    databases, or vector stores.
    """
    
    @abstractmethod
    async def add_message(self, session_id: str, message: Message) -> None:
        """Add a message to the memory backend.
        
        Args:
            session_id: Unique identifier for the conversation session
            message: The message to store
        """
        pass
    
    @abstractmethod
    async def get_messages(self, session_id: str, limit: Optional[int] = None) -> MessageList:
        """Retrieve messages from the memory backend.
        
        Args:
            session_id: Unique identifier for the conversation session  
            limit: Maximum number of recent messages to retrieve
            
        Returns:
            List of messages in chronological order
        """
        pass
    
    @abstractmethod
    async def clear_session(self, session_id: str) -> None:
        """Clear all messages for a session.
        
        Args:
            session_id: Unique identifier for the conversation session
        """
        pass
    
    @abstractmethod
    async def get_session_count(self, session_id: str) -> int:
        """Get the number of messages in a session.
        
        Args:
            session_id: Unique identifier for the conversation session
            
        Returns:
            Number of messages in the session
        """
        pass


class DictMemory(MemoryBackend):
    """In-memory dictionary-based storage backend.
    
    This is the simplest and fastest memory backend, storing all messages
    in a Python dictionary. Data is lost when the process ends.
    
    Attributes:
        max_messages: Maximum number of messages to keep per session
    """
    
    def __init__(self, max_messages: int = 1000):
        """Initialize the dictionary memory backend.
        
        Args:
            max_messages: Maximum messages to keep per session (default: 1000)
        """
        self.max_messages = max_messages
        self._sessions: Dict[str, List[Message]] = {}
    
    async def add_message(self, session_id: str, message: Message) -> None:
        """Add a message to memory."""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        
        self._sessions[session_id].append(message)
        
        # Trim old messages if we exceed max_messages
        if len(self._sessions[session_id]) > self.max_messages:
            self._sessions[session_id] = self._sessions[session_id][-self.max_messages:]
    
    async def get_messages(self, session_id: str, limit: Optional[int] = None) -> MessageList:
        """Retrieve messages from memory."""
        messages = self._sessions.get(session_id, [])
        
        if limit is not None:
            messages = messages[-limit:]
            
        return messages
    
    async def clear_session(self, session_id: str) -> None:
        """Clear all messages for a session."""
        self._sessions.pop(session_id, None)
    
    async def get_session_count(self, session_id: str) -> int:
        """Get the number of messages in a session."""
        return len(self._sessions.get(session_id, []))


class SQLiteMemory(MemoryBackend):
    """SQLite-based persistent storage backend.
    
    This backend stores messages in a SQLite database, providing persistence
    across application restarts. Suitable for production use with moderate
    message volumes.
    
    Attributes:
        db_path: Path to the SQLite database file
        max_messages: Maximum number of messages to keep per session
    """
    
    def __init__(self, db_path: str = "memory.db", max_messages: int = 10000):
        """Initialize the SQLite memory backend.
        
        Args:
            db_path: Path to SQLite database file (default: "memory.db")
            max_messages: Maximum messages to keep per session (default: 10000)
        """
        self.db_path = Path(db_path)
        self.max_messages = max_messages
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize the SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    timestamp TEXT NOT NULL,
                    agent_name TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_timestamp 
                ON messages(session_id, timestamp)
            """)
            conn.commit()
    
    async def add_message(self, session_id: str, message: Message) -> None:
        """Add a message to the SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO messages (session_id, role, content, metadata, timestamp, agent_name)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                message.role.value,
                message.content,
                json.dumps(message.metadata),
                message.timestamp.isoformat(),
                message.agent_name,
            ))
            
            # Clean up old messages if we exceed the limit
            conn.execute("""
                DELETE FROM messages 
                WHERE session_id = ? AND id NOT IN (
                    SELECT id FROM messages 
                    WHERE session_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                )
            """, (session_id, session_id, self.max_messages))
            
            conn.commit()
    
    async def get_messages(self, session_id: str, limit: Optional[int] = None) -> MessageList:
        """Retrieve messages from the SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = """
                SELECT role, content, metadata, timestamp, agent_name
                FROM messages 
                WHERE session_id = ? 
                ORDER BY timestamp ASC
            """
            params: List[Any] = [session_id]
            
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                message = Message(
                    role=row["role"],
                    content=row["content"],
                    metadata=json.loads(row["metadata"] or "{}"),
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    agent_name=row["agent_name"],
                )
                messages.append(message)
            
            return messages
    
    async def clear_session(self, session_id: str) -> None:
        """Clear all messages for a session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.commit()
    
    async def get_session_count(self, session_id: str) -> int:
        """Get the number of messages in a session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE session_id = ?",
                (session_id,)
            )
            return cursor.fetchone()[0]
    
    def close(self) -> None:
        """Close any database connections (for cleanup)."""
        # SQLite connections are closed automatically with context managers
        # This method exists for interface consistency
        pass
class VectorMemory(MemoryBackend):
    """Vector-based semantic memory backend (placeholder).
    
    This backend will store messages with vector embeddings for semantic
    similarity search. Currently a placeholder for future implementation.
    """
    
    def __init__(self, embedding_model: str = "text-embedding-ada-002"):
        """Initialize the vector memory backend.
        
        Args:
            embedding_model: Model to use for generating embeddings
        """
        self.embedding_model = embedding_model
        raise NotImplementedError("Vector memory backend coming in v0.2.0")
    
    async def add_message(self, session_id: str, message: Message) -> None:
        """Add a message with vector embedding."""
        raise NotImplementedError("Vector memory backend coming in v0.2.0")
    
    async def get_messages(self, session_id: str, limit: Optional[int] = None) -> MessageList:
        """Retrieve semantically similar messages."""
        raise NotImplementedError("Vector memory backend coming in v0.2.0")
    
    async def clear_session(self, session_id: str) -> None:
        """Clear all messages for a session."""
        raise NotImplementedError("Vector memory backend coming in v0.2.0")
    
    async def get_session_count(self, session_id: str) -> int:
        """Get the number of messages in a session."""
        raise NotImplementedError("Vector memory backend coming in v0.2.0")


def create_memory_backend(backend_type: str, **kwargs) -> MemoryBackend:
    """Factory function to create memory backends.
    
    Args:
        backend_type: Type of backend ("dict", "sqlite", "vector")
        **kwargs: Additional arguments for the backend constructor
        
    Returns:
        Initialized memory backend instance
        
    Raises:
        ValueError: If backend_type is not supported
    """
    backends = {
        "dict": DictMemory,
        "sqlite": SQLiteMemory,
        "vector": VectorMemory,
    }
    
    if backend_type not in backends:
        raise ValueError(f"Unsupported backend type: {backend_type}. "
                        f"Available: {list(backends.keys())}")
    
    return backends[backend_type](**kwargs)
