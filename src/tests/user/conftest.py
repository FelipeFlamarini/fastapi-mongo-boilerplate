from fastapi.testclient import TestClient
import pytest


@pytest.fixture(scope="module")
def first_user(client: TestClient) -> dict:
    response = client.get("/user")
    return response.json()[0]


@pytest.fixture(scope="package")
def route_prefix() -> str:
    return "/user"
