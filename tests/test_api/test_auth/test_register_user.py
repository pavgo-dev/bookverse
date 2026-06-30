import pytest
from httpx import AsyncClient


async def test_success(client: AsyncClient, user_data: dict):
    response = await client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == "Alex Doe"
    assert "id" in data
    assert data["is_admin"] is False


async def test_duplicate_email(client: AsyncClient, user_data: dict):
    await client.post("/api/v1/auth/register", json=user_data)

    response = await client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


@pytest.mark.parametrize(
    ("field_to_update", "new_value", "expected_error"),
    [
        ("confirm_password", "WrongPassword123", "Passwords do not match"),
        ("password", "NoDigitsPassword", "Password must contain at least one digit"),
        ("password", "lowercase123", "Password must contain at least one uppercase letter"),
        ("full_name", "admin", "Name is reserved"),
        ("password", "Sh1", "Value should have at least 8 items"),
    ],
)
async def test_validation_errors(client: AsyncClient, user_data: dict, field_to_update, new_value, expected_error):
    invalid_data = user_data.copy()
    invalid_data[field_to_update] = new_value

    if field_to_update == "password" and len(new_value) >= 8:
        invalid_data["confirm_password"] = new_value

    response = await client.post("/api/v1/auth/register", json=invalid_data)

    assert response.status_code == 422
    assert expected_error in response.text
