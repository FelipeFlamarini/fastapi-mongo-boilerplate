from typing import Optional
import re

from pydantic import BaseModel, EmailStr, Field, field_validator
from beanie import PydanticObjectId

from src.core.security import validate_password_strength


class UserReturn(BaseModel):
    id: PydanticObjectId
    email: EmailStr
    name: Optional[str]
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    def validate_password(cls, password):
        return validate_password_strength(password)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=64)


class UserDelete(BaseModel):
    id: PydanticObjectId
