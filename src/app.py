from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core.db import init_db
from src.api.routers import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await init_db()
    yield
    print("Shutting down gracefully...")


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(auth_router)
