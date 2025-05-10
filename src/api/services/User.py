from pymongo.errors import DuplicateKeyError
from beanie import PydanticObjectId

from src.api.repositories.User import UserRepository
from src.api.models import User
from src.core.exceptions import (
    NotFoundException,
    ConflictException,
    UnauthorizedException,
)
from src.core.security import verify_password


class UserService:
    @staticmethod
    async def find_all_users() -> list[User]:
        return await UserRepository.find_all_users()

    @staticmethod
    async def find_user_by_id(user_id) -> User:
        user = await UserRepository.find_user_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")
        return user

    @staticmethod
    async def create_user(email: str, plain_password: str) -> User:
        try:
            user = await UserRepository.create_user(email, plain_password)
        except DuplicateKeyError as e:
            raise ConflictException(f"User with email {email} already exists")
        return user

    @staticmethod
    async def update_user(
        user_id: PydanticObjectId,
        name: str | None = None,
        plain_password: str | None = None,
        is_active: bool | None = None,
    ) -> User:
        user = await UserRepository.find_user_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")

    @staticmethod
    async def authenticate_user(email: str, plain_password: str) -> User:
        user = await UserRepository.find_user_by_email(email)
        if not user:
            raise UnauthorizedException(f"Email or password is incorrect")
        if not verify_password(plain_password, user.hashed_password):
            raise UnauthorizedException(f"Email or password is incorrect")
        return user
