from httpx import AsyncClient


async def test_success(client: AsyncClient, user_data: dict):
    await client.post("/api/v1/auth/register", json=user_data)

    login_data = {"email": user_data["email"], "password": user_data["password"]}
    login_res = await client.post("/api/v1/auth/login", json=login_data)
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    password_data = {
        "old_password": user_data["password"],
        "new_password": "BrandNewPassword123",
        "confirm_password": "BrandNewPassword123",
    }

    response = await client.patch("/api/v1/auth/me/password", json=password_data, headers=headers)
    assert response.status_code == 204

    bad_login_res = await client.post("/api/v1/auth/login", json=login_data)
    assert bad_login_res.status_code == 401

    good_login_res = await client.post(
        "/api/v1/auth/login", json={"email": user_data["email"], "password": "BrandNewPassword123"}
    )
    assert good_login_res.status_code == 200


async def test_incorrect_oldpassword(client: AsyncClient, user_data: dict):
    await client.post("/api/v1/auth/register", json=user_data)
    login_res = await client.post(
        "/api/v1/auth/login", json={"email": user_data["email"], "password": user_data["password"]}
    )
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    bad_password_data = {
        "old_password": "WrongOldPassword1",
        "new_password": "BrandNewPassword123",
        "confirm_password": "BrandNewPassword123",
    }
    response = await client.patch("/api/v1/auth/me/password", json=bad_password_data, headers=headers)

    assert response.status_code == 400
    assert "Incorrect old password" in response.json()["detail"]
