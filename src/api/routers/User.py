from typing import Optional, Annotated
from fastapi import APIRouter, Depends
from beanie import PydanticObjectId

from src.api.services import UserService
from src.api.schemas import UserReturn, UserCreate
from src.api.dependencies import get_current_active_user

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("/", response_model=list[UserReturn])
async def find_all_users(
    current_user: Annotated[UserReturn, Depends(get_current_active_user)],
) -> list[UserReturn]:
    return await UserService.find_all_users()


@user_router.get("/{user_id}", response_model=UserReturn)
async def find_user_by_id(user_id: PydanticObjectId) -> UserReturn:
    return await UserService.find_user_by_id(user_id)


@user_router.post("/", response_model=UserReturn)
async def create_user(user: UserCreate) -> UserReturn:
    return await UserService.create_user(user.email, user.password)


@user_router.patch("/{user_id}", response_model=UserReturn)
async def update_user(
    user_id: PydanticObjectId,
    name: Optional[str] = None,
    password: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
    is_verified: Optional[bool] = None,
) -> UserReturn:
    return await UserService.update_user(
        user_id,
        name=name,
        plain_password=password,
        is_active=is_active,
        is_superuser=is_superuser,
        is_verified=is_verified,
    )
