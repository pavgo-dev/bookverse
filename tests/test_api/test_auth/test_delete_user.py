from httpx import AsyncClient


async def test_success(client: AsyncClient, user_data: dict):
    await client.post("/api/v1/auth/register", json=user_data)

    login_data = {"email": user_data["email"], "password": user_data["password"]}
    login_res = await client.post("/api/v1/auth/login", json=login_data)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    delete_res = await client.delete("/api/v1/auth/me", headers=headers)
    assert delete_res.status_code == 204

    check_res = await client.get("/api/v1/auth/me", headers=headers)
    assert check_res.status_code == 401
