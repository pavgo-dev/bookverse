from httpx import AsyncClient


async def test_without_filters(client: AsyncClient, sample_books):
    response = await client.get("/api/v1/books")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 3
    assert len(data["books"]) == 3
    assert data["books"][0]["title"] == "FastAPI Web Development"
    assert data["books"][1]["title"] == "Mastering Python"


async def test_filter_by_title(client: AsyncClient, sample_books):
    response = await client.get("/api/v1/books", params={"title": "Mastering"})

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["books"][0]["title"] == "Mastering Python"


async def test_filter_by_author(client: AsyncClient, sample_books):
    response = await client.get("/api/v1/books", params={"author": "John Doe"})

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 2
    assert all(book["author"] == "John Doe" for book in data["books"])


async def test_filter_by_year(client: AsyncClient, sample_books):
    response = await client.get("/api/v1/books", params={"year_min": 2023, "year_max": 2026})

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 2


async def test_pagination(client: AsyncClient, sample_books):
    response = await client.get("/api/v1/books", params={"limit": 1, "offset": 1})

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 3
    assert len(data["books"]) == 1
