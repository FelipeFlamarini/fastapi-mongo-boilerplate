from fastapi.testclient import TestClient
import pytest

from src.api.schemas import UserReturn


def test_get_activation_token_unauthorized(client: TestClient, route_prefix: str):
    response = client.get(
        f"{route_prefix}/activate", headers={"Authorization": "invalid_token"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.fixture(scope="function")
def activation_token(client: TestClient, route_prefix: str):
    response = client.get(f"{route_prefix}/activate")
    assert response.status_code == 200

    data = response.json()
    assert "activation_token" in response.json()

    return data["activation_token"]


def test_activate_user(
    client: TestClient,
    route_prefix: str,
    activation_token: str,
):
    response = client.patch(
        f"{route_prefix}/activate", json={"activation_token": activation_token}
    )
    assert response.status_code == 200
    assert UserReturn.model_validate(response.json())


def test_activate_user_invalid_token(
    client: TestClient,
    route_prefix: str,
):
    response = client.patch(
        f"{route_prefix}/activate", json={"activation_token": "invalid_token"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()
