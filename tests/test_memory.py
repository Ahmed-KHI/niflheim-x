"""
Tests for memory backends.
"""

import pytest
import tempfile
import os
from pathlib import Path

from niflheim_x.core.memory import (
    DictMemory, 
    SQLiteMemory, 
    create_memory_backend
)
from niflheim_x.core.types import Message, MessageRole


class TestDictMemory:
    """Test in-memory dictionary backend."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.memory = DictMemory(max_messages=10)
        self.session_id = "test_session"
    
    @pytest.mark.asyncio
    async def test_add_and_get_message(self):
        """Test adding and retrieving messages."""
        message = Message(
            role=MessageRole.USER,
            content="Hello"
        )
        
        await self.memory.add_message(self.session_id, message)
        messages = await self.memory.get_messages(self.session_id)
        
        assert len(messages) == 1
        assert messages[0].content == "Hello"
        assert messages[0].role == MessageRole.USER
    
    @pytest.mark.asyncio
    async def test_multiple_messages(self):
        """Test adding multiple messages."""
        messages = [
            Message(role=MessageRole.USER, content="Hello"),
            Message(role=MessageRole.ASSISTANT, content="Hi there!"),
            Message(role=MessageRole.USER, content="How are you?")
        ]
        
        for msg in messages:
            await self.memory.add_message(self.session_id, msg)
        
        retrieved = await self.memory.get_messages(self.session_id)
        assert len(retrieved) == 3
        assert retrieved[0].content == "Hello"
        assert retrieved[2].content == "How are you?"
    
    @pytest.mark.asyncio
    async def test_message_limit(self):
        """Test message limit enforcement."""
        # Add more messages than the limit
        for i in range(15):
            message = Message(
                role=MessageRole.USER,
                content=f"Message {i}"
            )
            await self.memory.add_message(self.session_id, message)
        
        messages = await self.memory.get_messages(self.session_id)
        assert len(messages) == 10  # Should be limited to max_messages
        assert messages[0].content == "Message 5"  # Should keep the latest 10
        assert messages[-1].content == "Message 14"
    
    @pytest.mark.asyncio
    async def test_get_messages_with_limit(self):
        """Test retrieving messages with limit."""
        for i in range(5):
            message = Message(
                role=MessageRole.USER,
                content=f"Message {i}"
            )
            await self.memory.add_message(self.session_id, message)
        
        messages = await self.memory.get_messages(self.session_id, limit=3)
        assert len(messages) == 3
        assert messages[0].content == "Message 2"  # Last 3 messages
        assert messages[-1].content == "Message 4"
    
    @pytest.mark.asyncio
    async def test_clear_session(self):
        """Test clearing session messages."""
        message = Message(role=MessageRole.USER, content="Test")
        await self.memory.add_message(self.session_id, message)
        
        assert await self.memory.get_session_count(self.session_id) == 1
        
        await self.memory.clear_session(self.session_id)
        
        assert await self.memory.get_session_count(self.session_id) == 0
        messages = await self.memory.get_messages(self.session_id)
        assert len(messages) == 0
    
    @pytest.mark.asyncio
    async def test_multiple_sessions(self):
        """Test handling multiple sessions."""
        session1 = "session_1"
        session2 = "session_2"
        
        msg1 = Message(role=MessageRole.USER, content="Session 1 message")
        msg2 = Message(role=MessageRole.USER, content="Session 2 message")
        
        await self.memory.add_message(session1, msg1)
        await self.memory.add_message(session2, msg2)
        
        messages1 = await self.memory.get_messages(session1)
        messages2 = await self.memory.get_messages(session2)
        
        assert len(messages1) == 1
        assert len(messages2) == 1
        assert messages1[0].content == "Session 1 message"
        assert messages2[0].content == "Session 2 message"


class TestSQLiteMemory:
    """Test SQLite database backend."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.memory = SQLiteMemory(db_path=self.db_path, max_messages=10)
        self.session_id = "test_session"
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Close the memory backend first
        if hasattr(self, 'memory'):
            self.memory.close()
        
        # Try to remove the database file with retry for Windows
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                # On Windows, sometimes the file is still locked
                # This is not critical for tests, so we can ignore it
                pass
        
        try:
            os.rmdir(self.temp_dir)
        except OSError:
            # Directory may not be empty or still locked
            pass
    
    @pytest.mark.asyncio
    async def test_add_and_get_message(self):
        """Test adding and retrieving messages."""
        message = Message(
            role=MessageRole.USER,
            content="Hello SQLite",
            metadata={"test": True}
        )
        
        await self.memory.add_message(self.session_id, message)
        messages = await self.memory.get_messages(self.session_id)
        
        assert len(messages) == 1
        assert messages[0].content == "Hello SQLite"
        assert messages[0].role == MessageRole.USER
        assert messages[0].metadata == {"test": True}
    
    @pytest.mark.asyncio
    async def test_persistence(self):
        """Test that data persists across memory instances."""
        message = Message(role=MessageRole.USER, content="Persistent message")
        await self.memory.add_message(self.session_id, message)
        
        # Create new memory instance with same database
        new_memory = SQLiteMemory(db_path=self.db_path)
        messages = await new_memory.get_messages(self.session_id)
        
        assert len(messages) == 1
        assert messages[0].content == "Persistent message"
    
    @pytest.mark.asyncio
    async def test_message_ordering(self):
        """Test that messages are returned in chronological order."""
        messages = [
            Message(role=MessageRole.USER, content="First"),
            Message(role=MessageRole.ASSISTANT, content="Second"),
            Message(role=MessageRole.USER, content="Third")
        ]
        
        for msg in messages:
            await self.memory.add_message(self.session_id, msg)
        
        retrieved = await self.memory.get_messages(self.session_id)
        assert len(retrieved) == 3
        assert retrieved[0].content == "First"
        assert retrieved[1].content == "Second"
        assert retrieved[2].content == "Third"
    
    @pytest.mark.asyncio
    async def test_message_limit_cleanup(self):
        """Test that old messages are cleaned up when limit is exceeded."""
        # Add more messages than the limit
        for i in range(15):
            message = Message(
                role=MessageRole.USER,
                content=f"Message {i}"
            )
            await self.memory.add_message(self.session_id, message)
        
        messages = await self.memory.get_messages(self.session_id)
        assert len(messages) == 10  # Should be limited to max_messages
        
        # Should keep the latest 10 messages
        assert messages[0].content == "Message 5"
        assert messages[-1].content == "Message 14"


class TestMemoryFactory:
    """Test memory backend factory function."""
    
    def test_create_dict_memory(self):
        """Test creating dictionary memory backend."""
        memory = create_memory_backend("dict", max_messages=50)
        
        assert isinstance(memory, DictMemory)
        assert memory.max_messages == 50
    
    def test_create_sqlite_memory(self):
        """Test creating SQLite memory backend."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
            db_path = temp_file.name
        
        try:
            memory = create_memory_backend("sqlite", db_path=db_path)
            assert isinstance(memory, SQLiteMemory)
            assert memory.db_path == Path(db_path)
            memory.close()  # Ensure connections are closed
        finally:
            # Handle Windows file deletion issues
            try:
                if os.path.exists(db_path):
                    os.remove(db_path)
            except PermissionError:
                # File might still be locked on Windows - not critical for test
                pass
    
    def test_invalid_backend_type(self):
        """Test error handling for invalid backend type."""
        with pytest.raises(ValueError, match="Unsupported backend type"):
            create_memory_backend("invalid_backend")


if __name__ == "__main__":
    pytest.main([__file__])
