from functools import lru_cache
from pydantic_settings import BaseSettings

from typing import Optional


class __Settings__(BaseSettings):
    frontend_url: Optional[str] = "http://localhost:3000"

    access_token_expire_minutes: Optional[int] = 10
    refresh_token_expire_days: Optional[int] = 7
    verification_token_expire_minutes: Optional[int] = 60
    activation_token_expire_minutes: Optional[int] = 60
    deactivation_token_expire_minutes: Optional[int] = 60
    lost_password_token_expire_minutes: Optional[int] = 60
    verification_code_length: Optional[int] = 6
    secret_key: str = "my_secret_key"
    algorithm: str = "HS256"
    timezone: Optional[int] = 0

    mongo_uri: str = "mongodb://root:changeme@db-test:27017"
    mongo_db_name: Optional[str] = "my-db"

    rabbitmq_url: Optional[str] = ""

    mailgun_api_key: Optional[str] = ""
    mailgun_domain: Optional[str] = ""
    mailgun_sender: Optional[str] = ""

    company_name: Optional[str] = "My Company"
    support_email: Optional[str] = "support@example.com"


@lru_cache
def get_settings() -> __Settings__:
    return __Settings__()
