from fastapi.testclient import TestClient
import pytest

from ..app import app
from ..core.db import init_db


@pytest.fixture(autouse=True)
async def setup():
    yield await init_db()


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def credentials_json() -> dict:
    return {"email": "test_login@email.com", "password": "Password123"}


@pytest.fixture
def credentials_data() -> dict:
    return {"username": "test_login@email.com", "password": "Password123"}


@pytest.fixture
def auth_tokens(client: TestClient, credentials_data: dict) -> dict:
    """Fixture that returns authentication tokens after login"""
    response = client.post("/auth/login", data=credentials_data)
    tokens = response.json()
    return {
        "access_token": tokens.get("access_token"),
        "refresh_token": tokens.get("refresh_token"),
        "token_type": tokens.get("token_type"),
    }


def test_create_user(client: TestClient, credentials_json: dict):
    response = client.post("/user", json=credentials_json)
    assert response.status_code == 200


def test_get_tokens(client: TestClient, credentials_data: dict):
    response = client.post("/auth/login", data=credentials_data)
    assert response.status_code == 200
    assert response.json().get("access_token") is not None
    assert response.json().get("token_type") == "bearer"


def test_refresh_token(client: TestClient, auth_tokens: dict):
    refresh_data = {"refresh_token": auth_tokens["refresh_token"]}
    response = client.post("/auth/refresh", json=refresh_data)
    assert response.status_code == 200
    assert response.json().get("access_token") is not None
