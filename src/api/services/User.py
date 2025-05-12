from beanie import PydanticObjectId
from pydantic import EmailStr

from src.api.repositories.User import UserRepository
from src.api.models import User
from src.api.schemas import UserUpdate
from src.core.exceptions import *


class UserService:
    @staticmethod
    async def find_all_users() -> list[User]:
        return await UserRepository.find_all_users()

    @staticmethod
    async def search_users(query: str, search_fields: list[str]) -> list[User]:
        results = []

        if "id" in search_fields:
            try:
                id_users = await UserRepository.search_users_by_id_pattern(query)
                if id_users:
                    for user in id_users:
                        if user not in results:
                            results.append(user)
            except:
                pass

        if "email" in search_fields:
            try:
                email_users = await UserRepository.search_users_by_email_pattern(query)
                if email_users:
                    for user in email_users:
                        if user not in results:
                            results.append(user)
            except:
                pass

        if "name" in search_fields:
            name_users = await UserRepository.search_users_by_name_pattern(query)
            if name_users:
                for user in name_users:
                    if user not in results:
                        results.append(user)

        return results

    @staticmethod
    async def find_user_by_email(email: EmailStr) -> User:
        user = await UserRepository.find_user_by_email(email)
        if not user:
            raise NotFoundException(f"User with email {email} not found")
        return user

    @staticmethod
    async def find_user_by_id(user_id: PydanticObjectId) -> User:
        user = await UserRepository.find_user_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")
        return user

    @staticmethod
    async def update_user_generic_details(
        user_id: PydanticObjectId, data: UserUpdate
    ) -> User:
        user = await UserRepository.find_user_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")

        update_data = {k: v for k, v in data.model_dump().items() if v is not None}

        if not update_data:
            return user

        return await UserRepository.update_user_generic_details(user, update_data)
