from datetime import timedelta
from typing import TYPE_CHECKING
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError

from fastapi.security import OAuth2PasswordRequestForm

from src.core.config import get_settings
from src.core.exceptions import *
from src.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_token,
)
from src.api.models import User
from src.api.services.User import UserService
from src.api.repositories import UserRepository
from src.types import TokenType


settings = get_settings()


class AuthService:
    @staticmethod
    async def __authenticate_user__(email: str, plain_password: str) -> User:
        user = await UserService.find_user_by_email(email)
        if not user:
            raise UnauthorizedException(f"Email or password is incorrect")
        if not verify_password(plain_password, user.hashed_password):
            raise UnauthorizedException(f"Email or password is incorrect")
        return user

    @staticmethod
    async def create_user(email: EmailStr, plain_password: str) -> User:
        try:
            user = await UserRepository.create_user(email, plain_password)
        except DuplicateKeyError as e:
            raise ConflictException(f"User with email {email} already exists")
        return user

    @staticmethod
    async def login(form_data: OAuth2PasswordRequestForm):
        user = await AuthService.__authenticate_user__(
            email=form_data.username, plain_password=form_data.password
        )

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )

        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    async def refresh_access_token(refresh_token: str):
        token_data = verify_token(token=refresh_token, token_type=TokenType.REFRESH)
        if not token_data:
            raise UnauthorizedException("Invalid refresh token")

        access_token = create_access_token(data={"sub": token_data.get("sub")})

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
