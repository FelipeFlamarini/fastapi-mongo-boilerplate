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
    async def update_user(user: User, **kwargs) -> User | None:
        allowed_fields = {
            "name", "hashed_password",
            "is_active", "is_superuser", "is_verified"
        }
        valid_updates = {k: v for k,
                         v in kwargs.items() if k in allowed_fields and v is not None}
        for key, value in valid_updates.items():
            setattr(user, key, value)
        if valid_updates:
            await user.save()
        return user
