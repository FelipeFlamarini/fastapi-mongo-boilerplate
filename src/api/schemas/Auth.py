from pydantic import BaseModel, field_validator, Field

from src.core.security import validate_password_strength


class AuthTokenLoginReturn(BaseModel):
    access_token: str
    token_type: str


class AuthTokenRefreshReturn(AuthTokenLoginReturn):
    pass


class AuthTokenVerification(BaseModel):
    verification_token: str


class AuthTokenVerificationReturn(AuthTokenVerification):
    pass


class AuthTokenActivation(BaseModel):
    activation_token: str


class AuthTokenActivationReturn(AuthTokenActivation):
    pass


class AuthTokenDeactivation(BaseModel):
    deactivation_token: str


class AuthTokenLostPassword(BaseModel):
    lost_password_token: str
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    def validate_password(cls, password):
        return validate_password_strength(password)


class AuthTokenLostPasswordReturn(BaseModel):
    lost_password_token: str


class AuthTokenDeactivationReturn(AuthTokenDeactivation):
    pass
