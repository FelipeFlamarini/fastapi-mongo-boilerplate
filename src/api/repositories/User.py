from beanie import PydanticObjectId

from src.api.models import User


class UserRepository:
    @staticmethod
    async def find_all_users() -> list[User]:
        return await User.find_all().to_list()

    @staticmethod
    async def find_user_by_id(user_id: PydanticObjectId) -> User | None:
        return await User.get(user_id)

    @staticmethod
    async def create_user(email: str, hashed_password: str) -> User | None:
        user = User(email=email, hashed_password=hashed_password)
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
