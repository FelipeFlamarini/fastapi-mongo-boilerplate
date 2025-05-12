from fastapi.testclient import TestClient


def test_verify_user_invalid_token(
    client: TestClient,
    route_prefix: str,
):
    response = client.patch(
        f"{route_prefix}/verify", json={"verification_token": "invalid_token"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()
