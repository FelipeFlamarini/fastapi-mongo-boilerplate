from pydantic import BaseModel


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


class AuthTokenDeactivationReturn(AuthTokenDeactivation):
    pass
