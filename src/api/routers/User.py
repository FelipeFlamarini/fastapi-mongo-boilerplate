from typing import Optional
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer
from beanie import PydanticObjectId
from pydantic import EmailStr

from src.api.services import UserService
from src.api.schemas import UserReturn

user_router = APIRouter(prefix="/user", tags=["user"])

__oauth2_scheme__ = OAuth2PasswordBearer(tokenUrl="token")


@user_router.get("/", response_model=list[UserReturn])
async def find_all_users() -> list[UserReturn]:
    return await UserService.find_all_users()


@user_router.get("/{user_id}", response_model=UserReturn)
async def find_user_by_id(
    user_id: PydanticObjectId
) -> UserReturn:
    return await UserService.find_user_by_id(user_id)


@user_router.post("/", response_model=UserReturn)
async def create_user(
    email: EmailStr,
    hashed_password: str
) -> UserReturn:
    return await UserService.create_user(email, hashed_password)


@user_router.patch("/{user_id}", response_model=UserReturn)
async def update_user(
    user_id: PydanticObjectId,
    name: Optional[str] = None,
    hashed_password: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
    is_verified: Optional[bool] = None
) -> UserReturn:
    return await UserService.update_user(
        user_id, name=name, hashed_password=hashed_password,
        is_active=is_active, is_superuser=is_superuser, is_verified=is_verified
    )
