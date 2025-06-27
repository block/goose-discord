import pytest
from src.agent_honk.thread_manager import ThreadManager


def test_thread_manager_basic():
    """Test basic thread manager functionality"""
    manager = ThreadManager()
    
    # Test registering a thread
    thread_id = "123456789"
    user_id = 987654321
    
    manager.register_thread(thread_id, user_id)
    
    # Test thread recognition
    assert manager.is_goose_thread(thread_id)
    assert not manager.is_goose_thread("nonexistent")
    
    # Test owner retrieval
    assert manager.get_thread_owner(thread_id) == user_id
    assert manager.get_thread_owner("nonexistent") is None
    
    # Test thread info
    info = manager.get_thread_info(thread_id)
    assert info is not None
    assert info['thread_id'] == thread_id
    assert info['owner_id'] == user_id
    
    # Test unregistering
    manager.unregister_thread(thread_id)
    assert not manager.is_goose_thread(thread_id)


def test_thread_manager_stats():
    """Test thread manager statistics"""
    manager = ThreadManager()
    
    # Add some threads
    manager.register_thread("thread1", 111)
    manager.register_thread("thread2", 222)
    manager.register_thread("thread3", 111)  # Same user
    
    stats = manager.get_stats()
    assert stats['total_active_threads'] == 3
    assert stats['unique_users'] == 2
    
    # Test user threads
    user_threads = manager.get_user_threads(111)
    assert len(user_threads) == 2
    assert "thread1" in user_threads
    assert "thread3" in user_threads
