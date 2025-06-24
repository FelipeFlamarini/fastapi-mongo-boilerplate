from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Awaitable

class QueueABC(ABC):
    """Abstract base class for queue implementations"""
    
    @abstractmethod
    def __init__(self, queue_name: str) -> None:
        """Initialize a queue with the given name"""
        pass
    
    @abstractmethod
    def publish(self, message: Dict[str, Any]) -> None:
        """Publish a message to the queue"""
        pass
    
    @abstractmethod
    def setup_consumer(self, callback: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """Set up a consumer with the given async callback"""
        pass
    
    @abstractmethod
    async def start_consuming(self) -> None:
        """Start consuming messages asynchronously"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the queue (and potentially the connection)"""
        pass
    
    @abstractmethod
    def declare_queue(self) -> None:
        """Declare/create the queue if it doesn't exist"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the queue name"""
        pass