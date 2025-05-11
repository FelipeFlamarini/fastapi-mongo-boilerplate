from fastapi.testclient import TestClient
import pytest
from beanie import PydanticObjectId

from src.api.schemas import UserReturn


def test_find_all_users(client: TestClient):
    response = client.get("/user", headers={"Authorization": ""})
    assert response.status_code == 401

    response = client.get("/user")
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(
        UserReturn.model_validate(user) for user in data
    ), "All items in the list should be of type UserReturn"


@pytest.fixture(scope="module")
def first_user_id(client: TestClient) -> PydanticObjectId:
    response = client.get("/user")
    return response.json()[0]["id"]


def test_get_user_by_id(client: TestClient, first_user_id: PydanticObjectId):
    response = client.get(f"/user/{first_user_id}")
    assert response.status_code == 200

    user_data = response.json()
    assert user_data["id"] == first_user_id
    assert UserReturn.model_validate(user_data)
