from fastapi.testclient import TestClient
import pytest

from src.api.schemas import UserReturn


def test_get_deactivation_token_unauthorized(client: TestClient, route_prefix: str):
    response = client.get(
        f"{route_prefix}/deactivate", headers={"Authorization": "invalid_token"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.fixture(scope="function")
def deactivation_token(client: TestClient, route_prefix: str):
    response = client.get(f"{route_prefix}/deactivate")
    assert response.status_code == 200

    data = response.json()
    assert "deactivation_token" in response.json()

    return data["deactivation_token"]


def test_deactivate_user(
    client: TestClient,
    route_prefix: str,
    deactivation_token: str,
):
    response = client.patch(
        f"{route_prefix}/deactivate", json={"deactivation_token": deactivation_token}
    )
    assert response.status_code == 200
    assert UserReturn.model_validate(response.json())
