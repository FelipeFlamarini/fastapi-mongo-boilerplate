from datetime import timedelta, datetime, UTC
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError
from beanie import PydanticObjectId
import random
import string

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
from src.core.email.email_queue_service import EmailQueueService


settings = get_settings()
email_service = EmailQueueService()


class AuthService:
    @staticmethod
    def generate_verification_code(length: int = None) -> str:
        """Generate a random verification code"""
        if length is None:
            length = settings.verification_code_length
        return ''.join(random.choices(string.digits, k=length))

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

            verification_code = AuthService.generate_verification_code()
            user.verification_code = verification_code
            user.verification_code_expires_at = datetime.now(
                UTC) + timedelta(minutes=settings.verification_token_expire_minutes)
            await user.save()

            await email_service.queue_email(
                to_email=email,
                subject="Verify your email address",
                template_name="verification_code",
                template_data={
                    "name": email.split("@")[0],
                    "code": verification_code
                }
            )

            return {
                "message": "Please check your email for the verification code"
            }
        except DuplicateKeyError as e:
            raise ConflictException(f"User with email {email} already exists")

    @staticmethod
    async def verify_user(verification_code: str, email: EmailStr) -> User:
        user = await UserService.find_user_by_email(email)
        if not user:
            raise NotFoundException("User not found")

        if not user.verification_code:
            raise UnauthorizedException(
                "No verification code found. Please request a new one.")

        expiry_time = user.verification_code_expires_at
        if expiry_time.tzinfo is None:
            expiry_time = expiry_time.replace(tzinfo=UTC)
        
        if expiry_time < datetime.now(UTC):
            raise UnauthorizedException(
                "Verification code has expired. Please request a new one.")

        if user.verification_code != verification_code:
            raise UnauthorizedException("Invalid verification code")

        user.verification_code = None
        user.verification_code_expires_at = None

        return await UserRepository.verify_user(user)

    @staticmethod
    async def resend_verification_code(email: EmailStr) -> None:
        user = await UserService.find_user_by_email(email)
        if not user:
            raise NotFoundException("User not found")

        if user.is_verified:
            raise ConflictException("User is already verified")

        verification_code = AuthService.generate_verification_code()
        user.verification_code = verification_code
        user.verification_code_expires_at = datetime.now(
            UTC) + timedelta(minutes=settings.verification_token_expire_minutes)
        await user.save()

        await email_service.queue_email(
            to_email=email,
            subject="Your new verification code",
            template_name="verification_code",
            template_data={
                "name": email.split("@")[0],
                "code": verification_code
            }
        )

        return {
            "message": "New verification code sent to your email"
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

        lost_password_token = create_token(
            data={"sub": str(user.id)},
            token_type=TokenType.LOST_PASSWORD,
        )

        base_url = settings.frontend_url
        await email_service.queue_email(
            to_email=email,
            subject="Password Reset Request",
            template_name="reset_password",
            template_data={
                "reset_url": f"{base_url}/reset-password?token={lost_password_token}"
            }
        )

        return {
            "lost_password_token": lost_password_token
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
