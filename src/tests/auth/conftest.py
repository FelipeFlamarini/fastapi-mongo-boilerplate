import pytest


def validate_new_token_response(data: dict) -> bool:
    return data.get("access_token") is not None and data.get("token_type") == "bearer"


@pytest.fixture(scope="package")
def route_prefix() -> str:
    return "/auth"
