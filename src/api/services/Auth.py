from datetime import timedelta
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError
from beanie import PydanticObjectId

from fastapi.security import OAuth2PasswordRequestForm

from src.core.config import get_settings
from src.core.exceptions import *
from src.core.security import (
    create_token,
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
        return {
            "verification_token": create_token(
                data={"sub": str(user.id)},
                token_type=TokenType.VERIFICATION
            )
        }

    @staticmethod
    async def login(form_data: OAuth2PasswordRequestForm):
        user = await AuthService.__authenticate_user__(
            email=form_data.username, plain_password=form_data.password
        )

        access_token = create_token(
            data={"sub": str(user.id)}, token_type=TokenType.ACCESS
        )

        refresh_token = create_token(
            data={"sub": str(user.id)}, token_type=TokenType.REFRESH
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    async def refresh_access_token(refresh_token: str):
        token_data = verify_token(
            token=refresh_token, token_type=TokenType.REFRESH)
        if not token_data:
            raise UnauthorizedException("Invalid refresh token")

        access_token = create_token(
            data={"sub": token_data.get("sub")}, token_type=TokenType.ACCESS
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    @staticmethod
    async def verify_user(verification_code: str) -> User:
        try:
            user_id = verify_token(
                verification_code, TokenType.VERIFICATION)["sub"]
        except Exception as e:
            raise UnauthorizedException("Invalid verification token") from e
        user = await UserRepository.find_user_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")

        return await UserRepository.verify_user(user)

    @staticmethod
    async def change_password(
        user_id: PydanticObjectId, current_password: str, new_password: str
    ) -> User:
        user = await UserRepository.find_user_by_id(user_id)

        if not user:
            raise NotFoundException(f"User with id {user_id} not found")

        if not verify_password(current_password, user.hashed_password):
            raise UnauthorizedException("Current password is incorrect")

        return await UserRepository.update_user_password(user, new_password)

    @staticmethod
    async def activate_user(activation_token: str) -> User:
        token_data = verify_token(activation_token, TokenType.ACTIVATION)
        if not token_data:
            raise UnauthorizedException("Invalid activation token")

        user_id = token_data["sub"]
        user = await UserRepository.find_user_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")

        return await UserRepository.activate_user(user)

    @staticmethod
    async def deactivate_user(deactivation_token: str) -> User:
        token_data = verify_token(deactivation_token, TokenType.DEACTIVATION)
        if not token_data:
            raise UnauthorizedException("Invalid activation token")

        user_id = token_data["sub"]
        user = await UserRepository.find_user_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")
        return await UserRepository.deactivate_user(user)

    @staticmethod
    async def get_activation_token(user: User) -> str:
        return {
            "activation_token": create_token(
                data={"sub": str(user.id)},
                token_type=TokenType.ACTIVATION,
            )
        }

    @staticmethod
    async def get_deactivation_token(user: User) -> str:
        return {
            "deactivation_token": create_token(
                data={"sub": str(user.id)},
                token_type=TokenType.DEACTIVATION,
            )
        }

    @staticmethod
    async def get_lost_password_token(email: EmailStr) -> str:
        user = await UserService.find_user_by_email(email)
        if not user:
            raise NotFoundException(f"User with email {email} not found")

        return {
            "lost_password_token": create_token(
                data={"sub": str(user.id)},
                token_type=TokenType.LOST_PASSWORD,
            )
        }

    @staticmethod
    async def change_lost_password(lost_password_token: str, new_password: str) -> User:
        token_data = verify_token(
            token=lost_password_token, token_type=TokenType.LOST_PASSWORD)
        if not token_data:
            raise UnauthorizedException("Invalid lost password token")

        user_id = token_data["sub"]
        user = await UserRepository.find_user_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")

        return await UserRepository.update_user_password(user, new_password)
