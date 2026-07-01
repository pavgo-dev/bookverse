from httpx import AsyncClient
from uuid_utils.compat import uuid7


async def test_success(client: AsyncClient, sample_books):
    target_book = sample_books[0]
    await client.post(f"/api/v1/favorites/{target_book.id}")

    response = await client.delete(f"/api/v1/favorites/{target_book.id}")

    assert response.status_code == 204


async def test_not_in_favorites(client: AsyncClient, sample_books):
    target_book = sample_books[0]

    response = await client.delete(f"/api/v1/favorites/{target_book.id}")

    assert response.status_code == 404
    assert "not in your favorites" in response.json()["detail"]


async def test_book_not_found(client: AsyncClient):
    random_id = uuid7()

    response = await client.delete(f"/api/v1/favorites/{random_id}")

    assert response.status_code == 404
    assert f"Book with id {random_id} not found" in response.json()["detail"]
