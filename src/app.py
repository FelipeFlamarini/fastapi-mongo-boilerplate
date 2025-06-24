from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from src.core.db import init_db
from src.core.email.email_queue_service import EmailQueueService
from src.api.routers import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await init_db()

    print("Starting email worker...")
    email_service = EmailQueueService()
    email_task = asyncio.create_task(email_service.start_consuming())
    app.state.email_task = email_task

    yield

    print("Shutting down gracefully...")
    # Cancel the email worker task
    if hasattr(app.state, "email_task"):
        app.state.email_task.cancel()
        try:
            await app.state.email_task
        except asyncio.CancelledError:
            print("Email worker stopped.")


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(auth_router)
