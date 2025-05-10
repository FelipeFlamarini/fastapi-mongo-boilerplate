from beanie import init_beanie
import motor.motor_asyncio

from src.core.config import get_settings
from src.api import models

settings = get_settings()


async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.mongo_uri)
    await init_beanie(database=client[settings.mongo_db_name], document_models=[models.User])
