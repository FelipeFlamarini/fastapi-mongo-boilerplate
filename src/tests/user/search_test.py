from fastapi.testclient import TestClient
import pytest

from src.api.schemas import UserReturn


@pytest.mark.parametrize(
    "test_id, query_params, expected_status, assertions",
    [
        (
            "search_by_exact_id",
            lambda first_user: {"query": first_user["id"], "search_fields": ["id"]},
            200,
            lambda data, first_user: any(
                user["id"] == first_user["id"] for user in data
            ),
        ),
        (
            "search_by_exact_email",
            lambda first_user: {
                "query": first_user["email"],
                "search_fields": ["email"],
            },
            200,
            lambda data, first_user: any(
                user["email"] == first_user["email"] for user in data
            ),
        ),
        (
            "search_by_exact_name",
            lambda first_user: {"query": first_user["name"], "search_fields": ["name"]},
            200,
            lambda data, first_user: any(
                user["name"] == first_user["name"] for user in data
            ),
        ),
        (
            "search_by_partial_name",
            lambda first_user: {
                "query": first_user["name"][:3],
                "search_fields": ["name"],
            },
            200,
            lambda data, first_user: len(data) > 0,
        ),
        (
            "search by_partial_email",
            lambda first_user: {
                "query": first_user["email"].split("@")[0],
                "search_fields": ["email"],
            },
            200,
            lambda data, first_user: len(data) > 0,
        ),
        (
            "search_multiple_fields",
            lambda first_user: {
                "query": first_user["email"][:3],
                "search_fields": ["email", "name"],
            },
            200,
            lambda data, first_user: isinstance(data, list),
        ),
        (
            "search_default_fields",
            lambda first_user: {"query": "test"},
            200,
            lambda data, first_user: isinstance(data, list),
        ),
        (
            "search_no_results",
            lambda first_user: {
                "query": "absolutely_no_user_should_have_this_in_any_field_12345"
            },
            200,
            lambda data, first_user: len(data) == 0,
        ),
        (
            "search_invalid_field",
            lambda first_user: {"query": "test", "search_fields": ["invalid_field"]},
            200,
            lambda data, first_user: isinstance(data, list),
        ),
        (
            "search_empty_query",
            lambda first_user: {"query": ""},
            200,
            lambda data, first_user: isinstance(data, list),
        ),
    ],
)
def test_search_users(
    client: TestClient,
    first_user: dict,
    route_prefix: str,
    test_id: str,
    query_params: callable,
    expected_status: int,
    assertions: callable,
):
    params = query_params(first_user)

    response = client.get(f"{route_prefix}/search", params=params)

    data = response.json()
    assert response.status_code == expected_status
    assert isinstance(data, list)

    assert all(
        UserReturn.model_validate(user) for user in data
    ), "All items in the list should be of type UserReturn"

    assert assertions(data, first_user), f"Assertions failed for test case {test_id}"
