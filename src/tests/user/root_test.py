from fastapi.testclient import TestClient

from src.api.schemas import UserReturn


def test_find_all_users_unauthorized(client: TestClient, route_prefix: str):
    response = client.get(f"{route_prefix}", headers={"Authorization": ""})
    assert response.status_code == 401


def test_find_all_users(client: TestClient, route_prefix: str):
    response = client.get(f"{route_prefix}")
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(
        UserReturn.model_validate(user) for user in data
    ), "All items in the list should be of type UserReturn"
