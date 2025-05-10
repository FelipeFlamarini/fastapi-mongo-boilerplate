from beanie import Document, Indexed
from typing import Annotated


class User(Document):
    email: Annotated[str, Indexed(unique=True)]
    hashed_password: str
    name: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Settings:
        collection = "users"
