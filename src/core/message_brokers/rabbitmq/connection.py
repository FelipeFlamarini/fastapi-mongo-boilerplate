import pika
from typing import Any
import threading

from ..abc.connection import QueueConnectionABC
from src.core.config import get_settings

settings = get_settings()


class RabbitMQConnection(QueueConnectionABC):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(RabbitMQConnection, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return

        self._connection = None
        self._channel = None
        self._url = settings.rabbitmq_url
        self._initialized = True
        self._connect()

    def _connect(self) -> None:
        """Establishes connection to RabbitMQ server"""
        try:
            parameters = pika.URLParameters(self._url)
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()
        except Exception as e:
            print(f"Error connecting to RabbitMQ: {str(e)}")
            raise

    @property
    def channel(self) -> Any:
        """Get the current channel, reconnecting if necessary"""
        if not self.is_connected():
            self._connect()
        return self._channel

    @property
    def connection(self) -> Any:
        """Get the current connection, reconnecting if necessary"""
        if not self.is_connected():
            self._connect()
        return self._connection

    def close(self) -> None:
        """Close the connection"""
        if self._connection and not self._connection.is_closed:
            self._connection.close()
            self._connection = None
            self._channel = None

    def is_connected(self) -> bool:
        """Check if the connection is active"""
        return self._connection is not None and not self._connection.is_closed
