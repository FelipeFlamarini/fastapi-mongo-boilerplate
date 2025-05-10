from typing import Annotated, Optional

from beanie import Document, Indexed
from pydantic import EmailStr


class User(Document):
    email: Annotated[EmailStr, Indexed(unique=True)]
    hashed_password: str
    name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Settings:
        collection = "users"
