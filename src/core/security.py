from datetime import datetime, timedelta, UTC
from passlib.context import CryptContext
import jwt

from fastapi.security import OAuth2PasswordBearer

from src.core.config import get_settings
from src.types import TokenType

settings = get_settings()


__pwd_context__ = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return __pwd_context__.verify(plain_password, hashed_password)


def _encode_jwt(data: dict) -> str:
    return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)


def get_password_hash(password: str) -> str:
    return __pwd_context__.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
    else:
        expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire, "token_type": TokenType.ACCESS})
    return _encode_jwt(to_encode)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
    else:
        expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
            days=settings.refresh_token_expire_days
        )
    to_encode.update({"exp": expire, "token_type": TokenType.REFRESH})
    return _encode_jwt(to_encode)


def verify_token(token: str, token_type: TokenType) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        if payload["token_type"] != token_type:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
