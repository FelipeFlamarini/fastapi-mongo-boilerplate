import pika
from typing import Callable
import json
from .queue import RabbitMQConnection


class RabbitMQBase:
    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self._connection_manager = RabbitMQConnection()
        self._connection_manager.channel.queue_declare(
            queue=self.queue_name, durable=True)

    @property
    def channel(self):
        return self._connection_manager.channel

    def publish(self, message: dict):
        """Publishes a message to the queue"""
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                )
            )
        except Exception as e:
            print(f"Error publishing message: {str(e)}")
            raise

    def consume(self, callback: Callable):
        """Sets up a consumer with the given callback"""
        try:
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=callback
            )
            print(
                f" [*] Waiting for messages in {self.queue_name} queue. To exit press CTRL+C")
            self.channel.start_consuming()
        except Exception as e:
            print(f"Error setting up consumer: {str(e)}")
            raise

    def close(self):
        """Closes the connection"""
        self._connection_manager.close()
