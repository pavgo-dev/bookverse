from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserOrm


async def test_success(client: AsyncClient, user_data: dict):
    await client.post("/api/v1/auth/register", json=user_data)

    login_data = {"email": user_data["email"], "password": user_data["password"]}
    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_wrong_credentials(client: AsyncClient, user_data: dict):
    await client.post("/api/v1/auth/register", json=user_data)

    wrong_login = {"email": user_data["email"], "password": "WrongPassword123"}
    response = await client.post("/api/v1/auth/login", json=wrong_login)

    assert response.status_code == 401
    assert "not correct" in response.json()["detail"]


async def test_banned(client: AsyncClient, db_session: AsyncSession, user_data: dict):
    await client.post("/api/v1/auth/register", json=user_data)

    query = select(UserOrm).where(UserOrm.email == user_data["email"])
    result = await db_session.execute(query)
    user = result.scalar_one()
    user.is_active = False
    await db_session.commit()

    login_data = {"email": user_data["email"], "password": user_data["password"]}
    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 403
    assert "banned" in response.json()["detail"]
