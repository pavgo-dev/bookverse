from httpx import AsyncClient


async def test_get_user_profile_success(client: AsyncClient, user_data: dict):
    await client.post("/api/v1/auth/register", json=user_data)

    login_data = {"email": user_data["email"], "password": user_data["password"]}
    login_res = await client.post("/api/v1/auth/login", json=login_data)
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == "Alex Doe"


async def test_get_user_profile_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401
