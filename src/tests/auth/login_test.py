from fastapi.testclient import TestClient
import pytest

from .conftest import validate_new_token_response


@pytest.mark.parametrize(
    "test_id,credentials_parametrized_data,expected_status,should_validate_token, should_expect_detail",
    [
        ("valid_login", {}, 200, True, False),
        (
            "invalid_login",
            {"username": "wrong_user", "password": "wrong_pass"},
            404,
            False,
            False,
        ),
        ("missing_username", {"password": "Password123"}, 422, False, True),
        ("missing_password", {"username": "im_missing_my_password"}, 422, False, True),
    ],
)
def test_login(
    client: TestClient,
    credentials_data: dict,
    route_prefix: str,
    test_id: str,
    credentials_parametrized_data: dict,
    expected_status: int,
    should_validate_token: bool,
    should_expect_detail: bool,
):
    response = client.post(
        f"{route_prefix}/login",
        data=(
            credentials_parametrized_data
            if credentials_parametrized_data
            else credentials_data
        ),
    )
    assert response.status_code == expected_status

    if should_validate_token and response.status_code == 200:
        assert response.cookies.get("refresh_token") is not None
        data = response.json()
        assert validate_new_token_response(
            data
        ), f"Token validation failed for test case: {test_id}"

    if should_expect_detail:
        data = response.json()
        assert (
            data.get("detail") is not None
        ), f"Detail not found for test case: {test_id}"
