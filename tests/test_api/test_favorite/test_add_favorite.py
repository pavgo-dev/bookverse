from httpx import AsyncClient
from uuid_utils.compat import uuid7


async def test_success(client: AsyncClient, sample_books, mock_user):
    target_book = sample_books[0]

    response = await client.post(f"/api/v1/favorites/{target_book.id}")

    assert response.status_code == 200
    data = response.json()

    assert data["book_id"] == str(target_book.id)
    assert data["user_id"] == str(mock_user.id)
    assert "added_at" in data


async def test_conflict(client: AsyncClient, sample_books):
    target_book = sample_books[0]

    await client.post(f"/api/v1/favorites/{target_book.id}")

    response = await client.post(f"/api/v1/favorites/{target_book.id}")

    assert response.status_code == 409
    assert "already in your favorites" in response.json()["detail"]


async def test_book_not_found(client: AsyncClient):
    random_id = uuid7()

    response = await client.post(f"/api/v1/favorites/{random_id}")

    assert response.status_code == 404
    assert "Book not found" in response.json()["detail"]
