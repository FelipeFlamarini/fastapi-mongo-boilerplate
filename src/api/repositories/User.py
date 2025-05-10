from beanie import PydanticObjectId
from pydantic import EmailStr

from src.api.models import User
from src.core.security import get_password_hash


class UserRepository:
    @staticmethod
    async def find_all_users() -> list[User]:
        return await User.find_all().to_list()

    @staticmethod
    async def find_user_by_id(user_id: PydanticObjectId) -> User | None:
        return await User.get(user_id)

    @staticmethod
    async def find_user_by_email(email: EmailStr) -> User | None:
        return await User.find_one(User.email == email)

    @staticmethod
    async def create_user(email: str, plain_password: str) -> User | None:
        user = User(
            email=email, hashed_password=get_password_hash(plain_password))
        await user.insert()
        return user

    @staticmethod
    async def update_user_name(user: User, name: str) -> User | None:
        user.name = name
        await user.save()
        return user

    @staticmethod
    async def update_user_password(user: User, plain_password: str) -> User | None:
        user.hashed_password = get_password_hash(plain_password)
        await user.save()
        return user

    @staticmethod
    async def activate_user(user: User) -> User | None:
        user.is_active = True
        await user.save()
        return user

    @staticmethod
    async def deactivate_user(user: User) -> User | None:
        user.is_active = False
        await user.save()
        return user

    @staticmethod
    async def superuser_user(user: User) -> User | None:
        user.is_superuser = True
        await user.save()
        return user

    @staticmethod
    async def unsuperuser_user(user: User) -> User | None:
        user.is_superuser = False
        await user.save()
        return user

    @staticmethod
    async def verify_user(user: User) -> User | None:
        user.is_verified = True
        await user.save()
        return user

    @staticmethod
    async def unverify_user(user: User) -> User | None:
        user.is_verified = False
        await user.save()
        return user
