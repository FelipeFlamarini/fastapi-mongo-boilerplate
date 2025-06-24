import sys
import os
from pathlib import Path

# Ensure project root is in sys.path before importing from src
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv()

from src.core.email.email_queue_service import EmailQueueService
import asyncio


async def main():
    """Main function to run the email worker"""
    email_service = EmailQueueService()
    print("Starting email worker...")
    await email_service.start_consuming()

if __name__ == "__main__":
    asyncio.run(main())
