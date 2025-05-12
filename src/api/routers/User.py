from typing import Annotated
from fastapi import APIRouter, Depends, Query

from src.api.services import UserService
from src.api.schemas import UserReturn, UserUpdate
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


@user_router.get("/me", response_model=UserReturn)
async def get_current_user(
    current_user: Annotated[UserReturn, Depends(get_current_active_user)],
) -> UserReturn:
    return current_user


@user_router.patch("/me", response_model=UserReturn)
async def update_user_details(
    current_user: Annotated[UserReturn, Depends(get_current_active_user)],
    data: UserUpdate,
) -> UserReturn:
    return await UserService.update_user_generic_details(current_user.id, data)
