from fastapi.testclient import TestClient
import pytest

from src.api.schemas import UserReturn


@pytest.mark.parametrize(
    "test_id,headers,expected_status,should_expect_detail",
    [
        ("valid_cookies", {}, 200, False),
        ("invalid_cookies", {"Authorization": "invalid_token"}, 401, True),
    ],
)
def test_get_me(
    client: TestClient,
    test_id: str,
    headers: dict,
    expected_status: int,
    should_expect_detail: bool,
):
    response = client.get("/user/me", headers=headers)
    assert response.status_code == expected_status

    if should_expect_detail:
        assert "detail" in response.json()
    else:
        assert UserReturn.model_validate(response.json())


@pytest.mark.parametrize(
    "test_id,body,expected_status,should_expect_detail",
    [
        ("invalid_name_0_length", {"name": ""}, 422, True),
        ("invalid_name_2_length", {"name": "Ab"}, 422, True),
        (
            "invalid_name_65_length",
            {
                "name": "abcdefghijklmnoqpqrstuvwxyz abcdefghijklmnoqpqrstuvwxyz 123456789"
            },
            422,
            True,
        ),
        ("valid_name_3_length", {"name": "Abc"}, 200, False),
        (
            "valid_name_64_length",
            {
                "name": "abcdefghijklmnoqpqrstuvwxyz abcdefghijklmnoqpqrstuvwxyz 12345678"
            },
            200,
            False,
        ),
    ],
)
def test_patch_me(
    client: TestClient,
    body: dict,
    test_id: str,
    expected_status: int,
    should_expect_detail: bool,
):
    response = client.patch(f"/user/me", json=body)
    assert response.status_code == expected_status

    if should_expect_detail:
        assert "detail" in response.json()
    else:
        assert UserReturn.model_validate(response.json())
