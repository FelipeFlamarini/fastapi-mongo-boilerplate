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


def test_create_user(client: TestClient):
    response = client.post(
        "/user", json={"email": "test@email.com", "password": "Password123"})
    assert response.status_code == 200


def test_create_user_conflict(client: TestClient):
    client.post(
        "/user", json={"email": "test_conflict@email.com", "password": "Password123"})

    response_conflict = client.post(
        "/user", json={"email": "test_conflict@email.com", "password": "Password123"})
    assert response_conflict.status_code == 409
