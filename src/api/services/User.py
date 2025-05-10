from pymongo.errors import DuplicateKeyError

from src.api.repositories.User import UserRepository
from src.api.models import User
from src.core import NotFoundException, ConflictException


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
    async def create_user(email: str, hashed_password: str) -> User:
        try:
            user = await UserRepository.create_user(email, hashed_password)
        except DuplicateKeyError as e:
            raise ConflictException(
                f"User with email {email} already exists") from e
        return user

    @staticmethod
    async def update_user(user_id, **kwargs) -> User:
        user = await UserRepository.find_user_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")
        return await UserRepository.update_user(user, **kwargs)
