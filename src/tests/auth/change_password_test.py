from fastapi.testclient import TestClient
import pytest

from src.api.schemas import UserReturn


@pytest.fixture(scope="module")
def new_password() -> str:
    return "NewPassword123"


@pytest.fixture(scope="module")
def route_name() -> str:
    return "change_password"


def test_change_password_unauthorized(
    client: TestClient,
    route_prefix: str,
    route_name: str
):
    response = client.patch(
        f"{route_prefix}/{route_name}", headers={"Authorization": "invalid_access_token"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def test_change_password(
    client: TestClient,
    route_prefix: str,
    route_name: str,
    credentials_json: dict,
    new_password: str
):
    response = client.patch(
        f"{route_prefix}/{route_name}",
        json={"old_password": credentials_json["password"], "new_password": new_password})
    assert response.status_code == 200
    assert UserReturn.model_validate(response.json())


def test_change_password_back(
    client: TestClient,
    route_prefix: str,
    route_name: str,
    credentials_json: dict,
    new_password: str
):
    response = client.patch(
        f"{route_prefix}/{route_name}",
        json={"old_password": new_password, "new_password": credentials_json["password"]})
    assert response.status_code == 200
    assert UserReturn.model_validate(response.json())


def test_change_password_invalid_old_password(
    client: TestClient,
    route_prefix: str,
    route_name: str,
    new_password: str
):
    response = client.patch(
        f"{route_prefix}/{route_name}",
        json={"old_password": "Invalid_0ld_password", "new_password": new_password})
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.parametrize(
    "test_id, new_password",
    [
        ("empty", ""),
        ("short", "Abcd123"),
        ("no_uppercase", "abcd1234"),
        ("no_lowercase", "ABCD1234"),
        ("no_number", "ABCDabcd"),
    ]
)
def test_change_password_invalid_new_password(
    client: TestClient,
    route_prefix: str,
    route_name: str,
    credentials_json: dict,
    test_id: str,
    new_password: str
):
    response = client.patch(
        f"{route_prefix}/{route_name}",
        json={"old_password": credentials_json["password"], "new_password": new_password})
    assert response.status_code == 422
    assert "detail" in response.json()
