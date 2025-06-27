import logging
from typing import Set, Dict, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ThreadManager:
    """Manages Discord thread state and ownership for Goose sessions"""
    
    def __init__(self):
        self.goose_threads: Set[str] = set()
        self.thread_owners: Dict[str, int] = {}  # thread_id -> user_id
        self.thread_created: Dict[str, datetime] = {}  # thread_id -> creation_time
        self.thread_last_activity: Dict[str, datetime] = {}  # thread_id -> last_message_time
    
    def register_thread(self, thread_id: str, user_id: int):
        """Register a new Goose thread"""
        self.goose_threads.add(thread_id)
        self.thread_owners[thread_id] = user_id
        now = datetime.now()
        self.thread_created[thread_id] = now
        self.thread_last_activity[thread_id] = now
        
        logger.info(f"Registered new Goose thread {thread_id} for user {user_id}")
    
    def is_goose_thread(self, thread_id: str) -> bool:
        """Check if a thread is a registered Goose thread"""
        return thread_id in self.goose_threads
    
    def get_thread_owner(self, thread_id: str) -> Optional[int]:
        """Get the owner of a thread"""
        return self.thread_owners.get(thread_id)
    
    def update_activity(self, thread_id: str):
        """Update the last activity time for a thread"""
        if thread_id in self.goose_threads:
            self.thread_last_activity[thread_id] = datetime.now()
    
    def unregister_thread(self, thread_id: str):
        """Remove a thread from tracking"""
        if thread_id in self.goose_threads:
            self.goose_threads.discard(thread_id)
            self.thread_owners.pop(thread_id, None)
            self.thread_created.pop(thread_id, None)
            self.thread_last_activity.pop(thread_id, None)
            logger.info(f"Unregistered Goose thread {thread_id}")
    
    def get_thread_info(self, thread_id: str) -> Optional[Dict]:
        """Get information about a thread"""
        if thread_id not in self.goose_threads:
            return None
            
        return {
            'thread_id': thread_id,
            'owner_id': self.thread_owners.get(thread_id),
            'created': self.thread_created.get(thread_id),
            'last_activity': self.thread_last_activity.get(thread_id)
        }
    
    def get_all_threads(self) -> List[Dict]:
        """Get information about all registered threads"""
        threads = []
        for thread_id in self.goose_threads:
            info = self.get_thread_info(thread_id)
            if info:
                threads.append(info)
        return threads
    
    def get_inactive_threads(self, hours: int = 24) -> List[str]:
        """Get threads that have been inactive for more than specified hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        inactive = []
        
        for thread_id, last_activity in self.thread_last_activity.items():
            if last_activity < cutoff:
                inactive.append(thread_id)
                
        return inactive
    
    def get_user_threads(self, user_id: int) -> List[str]:
        """Get all threads owned by a specific user"""
        return [
            thread_id for thread_id, owner_id in self.thread_owners.items()
            if owner_id == user_id
        ]
    
    def get_stats(self) -> Dict:
        """Get statistics about managed threads"""
        now = datetime.now()
        active_count = len(self.goose_threads)
        
        # Count threads by age
        recent_count = 0  # < 1 hour
        today_count = 0   # < 24 hours
        
        for created_time in self.thread_created.values():
            age = now - created_time
            if age < timedelta(hours=1):
                recent_count += 1
            if age < timedelta(hours=24):
                today_count += 1
        
        return {
            'total_active_threads': active_count,
            'threads_created_today': today_count,
            'threads_created_recently': recent_count,
            'unique_users': len(set(self.thread_owners.values()))
        }
