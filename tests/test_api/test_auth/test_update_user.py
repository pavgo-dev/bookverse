from httpx import AsyncClient


async def test_update_profile_success(client: AsyncClient, user_data: dict):
    await client.post("/api/v1/auth/register", json=user_data)

    login_data = {"email": user_data["email"], "password": user_data["password"]}
    login_res = await client.post("/api/v1/auth/login", json=login_data)
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    update_data = {"email": "new.email@example.com", "full_name": "John Doe Junior"}
    response = await client.patch("/api/v1/auth/me/profile", json=update_data, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new.email@example.com"
    assert data["full_name"] == "John Doe Junior"


async def test_update_profile_email_conflict(client: AsyncClient, user_data: dict):
    await client.post("/api/v1/auth/register", json=user_data)

    # Заменил email, что бы не делать линшюю фикстуру
    second_user = {**user_data, "email": "second@example.com"}
    await client.post("/api/v1/auth/register", json=second_user)

    login_res = await client.post(
        "/api/v1/auth/login", json={"email": "second@example.com", "password": user_data["password"]}
    )
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    update_data = {"email": user_data["email"]}
    response = await client.patch("/api/v1/auth/me/profile", json=update_data, headers=headers)

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]
