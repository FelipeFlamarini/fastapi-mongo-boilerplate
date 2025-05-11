import pytest
from fastapi.testclient import TestClient
from typing import Generator, Any

from ..core.db import init_db
from ..app import app


@pytest.fixture(autouse=True, scope="session")
async def setup():
    yield await init_db()


@pytest.fixture(autouse=True, scope="session")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True, scope="session")
def credentials_json() -> dict:
    return {"email": "test_login@email.com", "password": "Password123"}


@pytest.fixture(autouse=True, scope="session")
def credentials_data() -> dict:
    return {"username": "test_login@email.com", "password": "Password123"}


@pytest.fixture(autouse=True, scope="session")
def register_user(client: TestClient, credentials_json: dict) -> None:
    response = client.post("/auth/register", json=credentials_json)
    assert response.status_code == 200

    return None


@pytest.fixture(autouse=True, scope="session")
def auth_tokens(
    client: TestClient, credentials_data: dict, register_user: None
) -> None:
    response = client.post("/auth/login", data=credentials_data)
    assert response.status_code == 200

    token_data = response.json()
    access_token = token_data.get("access_token")
    token_type = token_data.get("token_type")
    assert access_token is not None
    assert token_type == "bearer"

    cookies = response.cookies
    refresh_token = cookies.get("refresh_token")
    assert refresh_token is not None

    client.cookies.set("refresh_token", refresh_token)
    client.headers.setdefault("Authorization", f"Bearer {access_token}")

    return None
