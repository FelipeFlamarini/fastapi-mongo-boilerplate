from abc import ABC, abstractmethod
from typing import Any

class QueueConnectionABC(ABC):
    """Abstract base class for queue connection implementations"""
    
    @abstractmethod
    def _connect(self) -> None:
        """Establish connection to the message broker"""
        pass
    
    @property
    @abstractmethod
    def channel(self) -> Any:
        """Get the current channel/communication interface"""
        pass
    
    @property
    @abstractmethod
    def connection(self) -> Any:
        """Get the current connection"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the connection"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the connection is active"""
        pass