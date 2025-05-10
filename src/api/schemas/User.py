from typing import Optional

from pydantic import BaseModel, EmailStr
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
    hashed_password: str


class UserUpdate(BaseModel):
    name: Optional[str]


class UserDelete(BaseModel):
    id: PydanticObjectId
