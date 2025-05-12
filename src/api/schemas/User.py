from typing import Optional
import re

from pydantic import BaseModel, EmailStr, Field, field_validator
from beanie import PydanticObjectId


class UserReturn(BaseModel):
    id: PydanticObjectId
    email: EmailStr
    name: Optional[str]
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)

    @field_validator("password")
    def validate_password_strength(cls, password):
        """Validate that the password contains at least 1 lowercase, 1 uppercase and 1 number"""
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one number")
        return password


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=64)


class UserDelete(BaseModel):
    id: PydanticObjectId
