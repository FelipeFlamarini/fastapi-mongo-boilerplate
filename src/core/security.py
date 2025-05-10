from passlib.context import CryptContext
from enum import Enum
import jwt

from datetime import datetime, timedelta, UTC
from core.config import get_settings

settings = get_settings()


__pwd_context__ = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


def get_password_hash(password: str) -> str:
    return __pwd_context__.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return __pwd_context__.verify(plain_password, hashed_password)


def encode_jwt(data: dict) -> str:
    return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)


async def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
    else:
        expire = datetime.now(UTC).replace(tzinfo=None) + \
            timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "token_type": TokenType.ACCESS})
    return encode_jwt(to_encode)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
    else:
        expire = datetime.now(UTC).replace(tzinfo=None) + \
            timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "token_type": TokenType.REFRESH})
    return encode_jwt(to_encode)
