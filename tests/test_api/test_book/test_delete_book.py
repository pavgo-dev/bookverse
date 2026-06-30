from httpx import AsyncClient
from uuid_utils.compat import uuid7


async def test_delete_book_success(client: AsyncClient, sample_books):
    target_book = sample_books[0]

    response = await client.delete(f"/api/v1/books/{target_book.id}")
    assert response.status_code == 204

    check_response = await client.get(f"/api/v1/books/{target_book.id}")
    assert check_response.status_code == 404


async def test_delete_book_not_found(client: AsyncClient, sample_books):
    random_id = uuid7()

    response = await client.delete(f"/api/v1/books/{random_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"
