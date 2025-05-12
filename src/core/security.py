from datetime import datetime, timedelta, UTC
import bcrypt
import jwt

from fastapi.security import OAuth2PasswordBearer

from src.core.config import get_settings
from src.types import TokenType

settings = get_settings()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def _encode_jwt(data: dict) -> str:
    return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_token(data: dict, token_type: TokenType):
    to_encode = data.copy()
    match token_type:
        case TokenType.ACCESS:
            expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        case TokenType.REFRESH:
            expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
                days=settings.refresh_token_expire_days
            )
        case TokenType.ACTIVATION:
            expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
                days=settings.activation_token_expire_minutes
            )
        case TokenType.DEACTIVATION:
            expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
                days=settings.deactivation_token_expire_minutes
            )
        case TokenType.VERIFICATION:
            expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
                days=settings.verification_token_expire_minutes
            )

    to_encode.update({"exp": expire, "token_type": token_type})
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
