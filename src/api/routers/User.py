from typing import Optional, Annotated
from fastapi import APIRouter, Depends, Query
from beanie import PydanticObjectId

from src.api.services import UserService
from src.api.schemas import UserReturn
from src.api.dependencies import get_current_active_user

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("/", response_model=list[UserReturn])
async def find_all_users(
    current_user: Annotated[UserReturn, Depends(get_current_active_user)],
) -> list[UserReturn]:
    return await UserService.find_all_users()


@user_router.get("/search", response_model=list[UserReturn])
async def search_users(
    current_user: Annotated[UserReturn, Depends(get_current_active_user)],
    query: str,
    search_fields: list[str] = Query(
        default=["id", "email", "name"],
        description="Fields to search in. Options: id, email, name, or any combination",
    ),
) -> list[UserReturn]:
    return await UserService.search_users(query, search_fields)


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
