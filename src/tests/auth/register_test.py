from fastapi.testclient import TestClient
import pytest


def test_register_user_success(client: TestClient, route_prefix: str):
    new_user = {"email": "another_test@email.com", "password": "Password123"}
    response = client.post(f"{route_prefix}/register", json=new_user)
    assert response.status_code == 200


def test_duplicate_registration(
    client: TestClient, credentials_json: dict, route_prefix: str
):
    response = client.post(f"{route_prefix}/register", json=credentials_json)
    assert response.status_code == 409


@pytest.mark.parametrize(
    "payload, expected_status, test_id",
    [
        (
            {"email": "test_all_valid@email.com", "password": "Password123"},
            200,
            "test_all_valid",
        ),
        ({"email": "invalid_email", "password": "Password123"}, 422, "invalid_email"),
        (
            {"email": "test_invalid_password_0_length@email.com", "password": ""},
            422,
            "invalid_password_0_length",
        ),
        (
            {
                "email": "test_invalid_password_7_length@email.com",
                "password": "1234567",
            },
            422,
            "invalid_password_7_length",
        ),
        (
            {
                "email": "test_invalid_password_no_lowercase@email.com",
                "password": "ABCD1234",
            },
            422,
            "invalid_password_no_lowercase",
        ),
        (
            {
                "email": "test_invalid_password_no_uppercase@email.com",
                "password": "abcd1234",
            },
            422,
            "invalid_password_no_uppercase",
        ),
        (
            {
                "email": "test_invalid_password_no_numbers@email.com",
                "password": "ABCDefgh",
            },
            422,
            "invalid_password_no_numbers",
        ),
        (
            {
                "email": "test_invalid_password_no_numbers@email.com",
                "password": "ABCDefgh",
            },
            422,
            "invalid_password_no_numbers",
        ),
        (
            {
                "email": "test_invalid_password_129_length@email.com",
                "password": "ABCDEFGHIJabcdefghij1234567890ABCDEFGHIJabcdefghij1234567890ABCDEFGHIJabcdefghij1234567890ABCDEFGHIJabcdefghij1234567890ABCDEFGHI",
            },
            422,
            "invalid_password_129_length",
        ),
        (
            {
                "email": "test_valid_password_8_length@email.com",
                "password": "ABCdef12",
            },
            200,
            "valid_password_8_length",
        ),
        (
            {
                "email": "test_valid_password_128_length@email.com",
                "password": "ABCDEFGHIJabcdefghij1234567890ABCDEFGHIJabcdefghij1234567890ABCDEFGHIJabcdefghij1234567890ABCDEFGHIJabcdefghij1234567890ABCDEFGH",
            },\
            200,
            "valid_password_128_length",
        ),
        ({"password": "Password123"}, 422, "missing_email"),
        ({"email": "test_missing_password@email.com"}, 422, "missing_password"),
        ({}, 422, "missing_all_fields"),
    ],
)
def test_create_user_invalid_inputs(
    client: TestClient, payload, expected_status, test_id, route_prefix: str
):
    response = client.post(f"{route_prefix}/register", json=payload)
    assert response.status_code == expected_status, f"Failed for case: {test_id}"


def test_create_user_conflict(client: TestClient, route_prefix: str):
    client.post(
        f"{route_prefix}/register",
        json={"email": "test_conflict@email.com", "password": "Password123"},
    )

    response_conflict = client.post(
        f"{route_prefix}/register",
        json={"email": "test_conflict@email.com", "password": "Password123"},
    )
    assert response_conflict.status_code == 409
