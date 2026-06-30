import pytest

import app.service.user as user_service


@pytest.fixture(autouse=True)
def mock_crypto_functions(monkeypatch):

    monkeypatch.setattr(user_service, "hash_password", lambda p: f"hashed_{p}")
    monkeypatch.setattr(user_service, "verify_password", lambda plain, hashed: f"hashed_{plain}" == hashed)


@pytest.fixture
def user_data() -> dict:
    return {
        "email": "alex.doe@example.com",
        "full_name": "Alex Doe",
        "password": "SecurePassword123",
        "confirm_password": "SecurePassword123",
    }
