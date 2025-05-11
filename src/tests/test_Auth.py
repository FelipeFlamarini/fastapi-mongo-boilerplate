from fastapi.testclient import TestClient
import pytest


def test_invalid_login(client: TestClient):
    invalid_credentials = {
        "username": "nonexistent@email.com",
        "password": "WrongPassword",
    }
    response = client.post("/auth/login", data=invalid_credentials)
    assert response.status_code == 404


def test_get_tokens(client: TestClient, credentials_data: dict):
    response = client.post("/auth/login", data=credentials_data)
    assert response.status_code == 200
    assert response.json().get("access_token") is not None
    assert response.json().get("token_type") == "bearer"


def test_refresh_token_with_access_token(client: TestClient):
    response = client.post("/auth/refresh")
    assert response.status_code == 200
    assert response.json().get("access_token") is not None
    assert response.json().get("token_type") == "bearer"


def test_refresh_token_without_access_token(client: TestClient):
    response = client.post("/auth/refresh", headers={"Authorization": ""})
    assert response.status_code == 200
    assert response.json().get("access_token") is not None
    assert response.json().get("token_type") == "bearer"


def test_invalid_refresh_token(client: TestClient):
    response = client.post(
        "/auth/refresh",
        cookies={"refresh_token": "invalid_refresh_token"},
    )
    assert response.status_code == 401


def test_missing_refresh_token(client: TestClient):
    response = client.post("/auth/refresh", cookies={"refresh_token": ""})
    assert response.status_code == 401


def test_register_user_success(client: TestClient):
    new_user = {"email": "another_test@email.com", "password": "Password123"}
    response = client.post("/auth/register", json=new_user)
    assert response.status_code == 200


def test_duplicate_registration(client: TestClient, credentials_json: dict):
    response = client.post("/auth/register", json=credentials_json)
    assert response.status_code == 409


@pytest.mark.parametrize(
    "payload,expected_status,test_id",
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
                "email": "test_invalid_password_33_length@email.com",
                "password": "ABCDEFGHIJabcdefghij1234567890abc",
            },
            422,
            "invalid_password_33_length",
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
                "email": "test_valid_password_32_length@email.com",
                "password": "ABCDEFGHIJabcdefghij1234567890ab",
            },
            200,
            "valid_password_32_length",
        ),
        ({"password": "Password123"}, 422, "missing_email"),
        ({"email": "test_missing_password@email.com"}, 422, "missing_password"),
        ({}, 422, "missing_all_fields"),
    ],
)
def test_create_user_invalid_inputs(
    client: TestClient, payload, expected_status, test_id
):
    response = client.post("/auth/register", json=payload)
    assert response.status_code == expected_status, f"Failed for case: {test_id}"


def test_create_user_conflict(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "test_conflict@email.com", "password": "Password123"},
    )

    response_conflict = client.post(
        "/auth/register",
        json={"email": "test_conflict@email.com", "password": "Password123"},
    )
    assert response_conflict.status_code == 409
