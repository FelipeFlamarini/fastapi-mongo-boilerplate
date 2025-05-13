from fastapi.testclient import TestClient
import pytest

from src.api.schemas import UserReturn


def get_lost_password_token_unauthorized(client: TestClient, route_prefix: str):
    response = client.get(
        f"{route_prefix}/password", headers={"Authorization": "invalid_token"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.fixture(scope="function")
def lost_password_token(client: TestClient, route_prefix: str):
    response = client.get(f"{route_prefix}/password")
    assert response.status_code == 200

    data = response.json()
    assert "lost_password_token" in data

    return data["lost_password_token"]


def test_lost_password(
    client: TestClient,
    route_prefix: str,
    password_token: str,
):
    response = client.patch(
        f"{route_prefix}/lost_password", json={"password_token": password_token, "new_password": "NewPassword123"}, headers={"Authorization": "invalid_access_token"}
    )
    assert response.status_code == 200
    assert UserReturn.model_validate(response.json())


def test_lost_password_invalid_token(
    client: TestClient,
    route_prefix: str,
):
    response = client.patch(
        f"{route_prefix}/lost_password", json={"password_token": "invalid_token", "new_password": "NewPassword123"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()
