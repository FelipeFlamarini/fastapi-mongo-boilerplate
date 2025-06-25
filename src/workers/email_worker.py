from src.core.email.email_queue_service import EmailQueueService
from src.core.config import get_settings
import signal
import asyncio
import sys
import os

# Add the project root to Python path BEFORE importing src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class EmailWorker:
    """Standalone email worker service"""

    def __init__(self):
        self.settings = get_settings()
        self.email_service = EmailQueueService()
        self._shutdown = False
        self._consuming_task = None

    async def start(self):
        """Start the email worker"""
        print("Starting email worker...")
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self._signal_handler)

        try:
            # Create a task for consuming so we can cancel it
            self._consuming_task = asyncio.create_task(
                self.email_service.start_consuming())
            await self._consuming_task
        except asyncio.CancelledError:
            print("Email worker consumption cancelled")
        except Exception as e:
            print(f"Error in email worker: {e}")
            raise

    def _signal_handler(self):
        """Handle shutdown signals"""
        print("Received shutdown signal, stopping email worker...")
        self._shutdown = True
        if self._consuming_task and not self._consuming_task.done():
            self._consuming_task.cancel()

    async def stop(self):
        """Stop the email worker gracefully"""
        print("Stopping email worker...")
        if self._consuming_task and not self._consuming_task.done():
            self._consuming_task.cancel()
            try:
                await self._consuming_task
            except asyncio.CancelledError:
                pass

        # Close the email service connection
        if hasattr(self.email_service, 'queue') and hasattr(self.email_service.queue, 'close'):
            self.email_service.queue.close()


async def main():
    """Main function to run the email worker"""
    worker = EmailWorker()

    try:
        await worker.start()
    except KeyboardInterrupt:
        print("\nReceived interrupt signal")
    finally:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
