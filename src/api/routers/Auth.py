from typing import Annotated

from fastapi import APIRouter, Response, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.core.config import get_settings
from src.core.exceptions import UnauthorizedException
from src.api.services import AuthService, UserService
from src.api.schemas import UserReturn, UserCreate


settings = get_settings()

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login")
async def login(
    response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    return_data = await AuthService.login(form_data=form_data)
    response.set_cookie(
        key="refresh_token",
        value=return_data["refresh_token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )
    return {
        "access_token": return_data["access_token"],
        "token_type": return_data["token_type"],
    }


@auth_router.post("/refresh")
async def refresh_access_token(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise UnauthorizedException("Refresh token not found")

    return await AuthService.refresh_access_token(refresh_token=refresh_token)


@auth_router.post("/register", response_model=UserReturn)
async def create_user(user: UserCreate) -> UserReturn:
    return await UserService.create_user(user.email, user.password)
