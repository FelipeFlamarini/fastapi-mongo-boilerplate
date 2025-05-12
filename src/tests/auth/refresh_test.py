from fastapi.testclient import TestClient
import pytest

from .conftest import validate_new_token_response


@pytest.mark.parametrize(
    "test_id,cookies,headers,expected_status,should_validate_token,should_expect_detail",
    [
        ("refresh_valid_cookies_and_headers", {}, {}, 200, True, False),
        ("refresh_only_cookies", {}, {"Authorization": ""}, 200, True, False),
        ("refresh_missing_refresh_token", {"refresh_token": ""}, {}, 401, False, True),
        (
            "refresh_invalid_cookies",
            {"refresh_token": "invalid_token"},
            {},
            401,
            False,
            True,
        ),
    ],
)
def test_refresh(
    client: TestClient,
    route_prefix: str,
    test_id: str,
    cookies: dict,
    headers: dict,
    expected_status: int,
    should_validate_token: bool,
    should_expect_detail: bool,
):
    response = client.post(f"{route_prefix}/refresh", cookies=cookies, headers=headers)
    assert response.status_code == expected_status

    if should_validate_token:
        data = response.json()
        assert validate_new_token_response(
            data
        ), f"Assertions failed for test case: {test_id}"

    if should_expect_detail:
        data = response.json()
        assert (
            data.get("detail") is not None
        ), f"Detail not found for test case: {test_id}"
