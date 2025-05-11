from fastapi.testclient import TestClient
import pytest
from beanie import PydanticObjectId

from src.api.schemas import UserReturn


@pytest.fixture(scope="module")
def first_user(client: TestClient) -> dict:
    response = client.get("/user")
    return response.json()[0]


@pytest.fixture(scope="module")
def route_prefix() -> str:
    return "/user"


def test_find_all_users(client: TestClient, route_prefix: str):
    response = client.get(f"{route_prefix}", headers={"Authorization": ""})
    assert response.status_code == 401

    response = client.get(f"{route_prefix}")
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(
        UserReturn.model_validate(user) for user in data
    ), "All items in the list should be of type UserReturn"


def test_search_users_unauthorized(client: TestClient, route_prefix: str):
    response = client.get(
        f"{route_prefix}/search",
        params={"query": "test"},
        headers={"Authorization": ""},
    )
    assert response.status_code == 401


def test_search_users_by_id(client: TestClient, first_user: dict, route_prefix: str):
    user_id = first_user["id"]

    response = client.get(
        f"{route_prefix}/search", params={"query": user_id, "search_fields": ["id"]}
    )
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(
        user["id"] == user_id for user in data
    ), "User with matching ID not found in results"
    assert all(
        UserReturn.model_validate(user) for user in data
    ), "All items in the list should be of type UserReturn"


def test_search_users_by_email(client: TestClient, first_user: dict, route_prefix: str):
    email = first_user["email"]

    response = client.get(
        f"{route_prefix}/search", params={"query": email, "search_fields": ["email"]}
    )
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(
        user["email"] == email for user in data
    ), "User with matching email not found in results"
    assert all(
        UserReturn.model_validate(user) for user in data
    ), "All items in the list should be of type UserReturn"


def test_search_users_by_name(client: TestClient, first_user: dict, route_prefix: str):
    if not first_user.get("name"):
        pytest.skip("First user has no name set")

    name = first_user["name"]

    response = client.get(
        f"{route_prefix}/search", params={"query": name, "search_fields": ["name"]}
    )
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(
        user["name"] == name for user in data
    ), "User with matching name not found in results"
    assert all(
        UserReturn.model_validate(user) for user in data
    ), "All items in the list should be of type UserReturn"


def test_search_users_by_partial_name(
    client: TestClient, first_user: dict, route_prefix: str
):
    if not first_user.get("name") or len(first_user["name"]) < 3:
        pytest.skip("First user has no name set or name is too short")

    partial_name = first_user["name"][:3]

    response = client.get(
        f"{route_prefix}/search",
        params={"query": partial_name, "search_fields": ["name"]},
    )
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(
        UserReturn.model_validate(user) for user in data
    ), "All items in the list should be of type UserReturn"


def test_search_users_multiple_fields(
    client: TestClient, first_user: dict, route_prefix: str
):
    query = first_user["email"][:3]  # Use part of email as query

    response = client.get(
        f"{route_prefix}/search",
        params={"query": query, "search_fields": ["email", "name"]},
    )
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert all(
        UserReturn.model_validate(user) for user in data
    ), "All items in the list should be of type UserReturn"


def test_search_users_default_fields(client: TestClient, route_prefix: str):
    response = client.get(
        f"{route_prefix}/search",
        params={"query": "test"},  # No search_fields specified, should use defaults
    )
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert all(
        UserReturn.model_validate(user) for user in data
    ), "All items in the list should be of type UserReturn"


def test_search_users_no_results(client: TestClient, route_prefix: str):
    response = client.get(
        f"{route_prefix}/search",
        params={"query": "absolutely_no_user_should_have_this_in_any_field_12345"},
    )
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 0


def test_search_users_invalid_search_field(client: TestClient, route_prefix: str):
    response = client.get(
        f"{route_prefix}/search",
        params={"query": "test", "search_fields": ["invalid_field"]},
    )
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)


def test_search_users_empty_query(client: TestClient, route_prefix: str):
    response = client.get(f"{route_prefix}/search", params={"query": ""})
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
