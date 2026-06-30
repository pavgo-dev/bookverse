from httpx import AsyncClient


async def test_success(client: AsyncClient):
    book_data = {
        "title": "Design Patterns",
        "author": "Erich Gamma",
        "published_year": 1994,
        "isbn": "9780201633610",
        "description": "Elements of Reusable Object-Oriented Software.",
        "cover_image_url": "https://example.com",
    }

    response = await client.post("/api/v1/books", json=book_data)

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["title"] == book_data["title"]
    assert data["isbn"] == book_data["isbn"]


async def test_conflict_isbn(client: AsyncClient, sample_books):
    existing_isbn = sample_books[0].isbn

    duplicate_data = {
        "title": "Some New Title",
        "author": "Some Author",
        "published_year": 2026,
        "isbn": existing_isbn,
        "description": "Trigger conflict",
        "cover_image_url": None,
    }

    response = await client.post("/api/v1/books", json=duplicate_data)

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]
