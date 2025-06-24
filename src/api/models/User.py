from typing import Annotated, Optional
from datetime import datetime, UTC
from beanie import Document, Indexed
from pydantic import EmailStr


class User(Document):
    email: Annotated[EmailStr, Indexed(unique=True)]
    hashed_password: str
    name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    verification_code: Optional[str] = None
    verification_code_expires_at: Optional[datetime] = None

    class Settings:
        collection = "users"
