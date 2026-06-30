from httpx import AsyncClient


async def test_empty(client: AsyncClient):
    response = await client.get("/api/v1/favorites")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 0
    assert data["books"] == []


async def test_success(client: AsyncClient, sample_books):
    await client.post(f"/api/v1/favorites/{sample_books[0].id}")
    await client.post(f"/api/v1/favorites/{sample_books[1].id}")

    response = await client.get("/api/v1/favorites")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 2
    assert len(data["books"]) == 2

    assert data["books"][0]["title"] == "FastAPI Guide"


async def test_pagination(client: AsyncClient, sample_books):
    await client.post(f"/api/v1/favorites/{sample_books[0].id}")
    await client.post(f"/api/v1/favorites/{sample_books[1].id}")

    response = await client.get("/api/v1/favorites", params={"limit": 1, "offset": 1})

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 2
    assert len(data["books"]) == 1
    assert data["books"][0]["title"] == "SQLAlchemy Masterclass"
