import pika
from typing import Any, Callable, Dict, Awaitable
import json
import asyncio
from .connection import RabbitMQConnection
from ..abc.queue import QueueABC


class RabbitMQQueue(QueueABC):
    def __init__(self, queue_name: str):
        self._queue_name = queue_name
        self._connection_manager = RabbitMQConnection()
        self._callback = None
        self.declare_queue()

    @property
    def name(self) -> str:
        return self._queue_name

    @property
    def channel(self):
        return self._connection_manager.channel

    def declare_queue(self) -> None:
        """Declares the queue with RabbitMQ"""
        self.channel.queue_declare(queue=self._queue_name, durable=True)

    def publish(self, message: Dict[str, Any]) -> None:
        """Publishes a message to the queue"""
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=self._queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                )
            )
        except Exception as e:
            print(f"Error publishing message: {str(e)}")
            raise

    async def process_message(self, channel, method, properties, body):
        """Process a single message asynchronously"""
        try:
            message = json.loads(body)
            if self._callback:
                await self._callback(message)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def setup_consumer(self, callback: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """Sets up the consumer without starting consumption"""
        self._callback = callback
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self._queue_name,
            on_message_callback=lambda ch, method, props, body: asyncio.create_task(
                self.process_message(ch, method, props, body)
            )
        )

    async def start_consuming(self) -> None:
        """Starts consuming messages asynchronously"""
        if not self._callback:
            raise RuntimeError("No callback set. Call setup_consumer first.")

        try:
            while True:
                # Check for cancellation
                if asyncio.current_task().cancelled():
                    break
                    
                try:
                    self.channel.connection.process_data_events(time_limit=0.1)
                    await asyncio.sleep(0.1)  # Give other tasks a chance to run
                except Exception as e:
                    print(f"Error consuming messages: {str(e)}")
                    break
        except asyncio.CancelledError:
            print("Message consumption cancelled")
            raise

    def close(self) -> None:
        """Closes the connection"""
        self._connection_manager.close()
