from pydantic import BaseModel


class AuthTokenLoginReturn(BaseModel):
    access_token: str
    token_type: str


class AuthTokenRefreshReturn(AuthTokenLoginReturn):
    pass


class AuthLogin(BaseModel):
    email: str
    password: str
