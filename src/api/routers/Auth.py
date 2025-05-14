from typing import Annotated

from fastapi import APIRouter, Response, Depends, Request, Query
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from src.core.config import get_settings
from src.core.exceptions import UnauthorizedException
from src.api.models import User
from src.api.services import AuthService
from src.api.schemas import (
    UserCreate,
    UserReturn,
    AuthTokenVerification,
    AuthTokenVerificationReturn,
    AuthTokenActivation,
    AuthTokenActivationReturn,
    AuthTokenDeactivation,
    AuthTokenDeactivationReturn,
    AuthTokenLostPassword,
    AuthTokenLostPasswordReturn,
)
from src.api.dependencies import get_current_user, get_current_active_user


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


@auth_router.post("/register", response_model=AuthTokenVerificationReturn)
async def create_user(user: UserCreate) -> AuthTokenVerificationReturn:
    return await AuthService.create_user(user.email, user.password)


@auth_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}


@auth_router.patch("/verify", response_model=UserReturn)
async def verify_token(data: AuthTokenVerification) -> UserReturn:
    return await AuthService.verify_user(data.verification_token)


@auth_router.get("/activate", response_model=AuthTokenActivationReturn)
async def get_activation_token(
    current_user: User = Depends(get_current_user),
) -> AuthTokenActivationReturn:
    return await AuthService.get_activation_token(current_user)


@auth_router.patch("/activate", response_model=UserReturn)
async def activate_token(data: AuthTokenActivation) -> UserReturn:
    return await AuthService.activate_user(data.activation_token)


@auth_router.get("/deactivate", response_model=AuthTokenDeactivationReturn)
async def get_deactivation_token(
    current_user: User = Depends(get_current_active_user),
) -> AuthTokenDeactivationReturn:
    return await AuthService.get_deactivation_token(current_user)


@auth_router.patch("/deactivate", response_model=UserReturn)
async def deactivate_token(data: AuthTokenDeactivation) -> UserReturn:
    return await AuthService.deactivate_user(data.deactivation_token)


@auth_router.get("/lost_password", response_model=AuthTokenLostPasswordReturn)
async def get_lost_password_token(
    email: EmailStr = Query(..., title="Email",
                            description="User email for lost password token")
) -> AuthTokenLostPasswordReturn:
    return await AuthService.get_lost_password_token(email)


@auth_router.patch("/lost_password", response_model=UserReturn)
async def lost_password_token(
    data: AuthTokenLostPassword
) -> UserReturn:
    return await AuthService.change_lost_password(data.lost_password_token, data.new_password)
