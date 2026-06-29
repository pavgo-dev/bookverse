from httpx import AsyncClient


async def test_get_all_books_success(client: AsyncClient, sample_books):
    response = await client.get("/api/v1/books")

    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 3
    assert len(data["books"]) == 3
