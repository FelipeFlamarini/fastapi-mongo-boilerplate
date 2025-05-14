from fastapi.testclient import TestClient
import pytest

from src.api.schemas import UserReturn


@pytest.fixture(scope="module")
def route_name() -> str:
    return "lost_password"


def get_lost_password_token_unauthorized(client: TestClient, route_prefix: str, route_name: str, credentials_json: dict):
    response = client.get(
        f"{route_prefix}/{route_name}", headers={"Authorization": "invalid_token"}, params={"email": credentials_json["email"]}
    )
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.fixture(scope="function")
def lost_password_token(client: TestClient, route_prefix: str, route_name: str, credentials_json: dict):
    response = client.get(f"{route_prefix}/{route_name}",
                          params={"email": credentials_json["email"]})
    assert response.status_code == 200

    data = response.json()
    assert "lost_password_token" in data

    return data["lost_password_token"]


def test_lost_password(
    client: TestClient,
    route_prefix: str,
    route_name: str,
    lost_password_token: str,
    credentials_json: dict,
):
    response = client.patch(
        f"{route_prefix}/{route_name}", json={"lost_password_token": lost_password_token, "new_password": credentials_json["password"]}
    )
    assert response.status_code == 200
    assert UserReturn.model_validate(response.json())


def test_lost_password_invalid_token(
    client: TestClient,
    route_prefix: str,
    route_name: str,
):
    response = client.patch(
        f"{route_prefix}/{route_name}", json={"lost_password_token": "invalid_token", "new_password": "NewPassword123"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()
