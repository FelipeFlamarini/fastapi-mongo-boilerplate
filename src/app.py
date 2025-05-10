from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core import init_db
from src.api.routers import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await init_db()
    yield
    print("Shutting down gracefully...")

app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
