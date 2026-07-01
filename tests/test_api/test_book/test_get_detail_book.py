from httpx import AsyncClient
from uuid_utils.compat import uuid7


async def test_success(client: AsyncClient, sample_books):
    target_book = sample_books[0]

    response = await client.get(f"/api/v1/books/{target_book.id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(target_book.id)
    assert data["title"] == target_book.title
    assert data["isbn"] == target_book.isbn
    assert data["avg_rating"] == 0.0
    assert data["reviews_qty"] == 0
    assert data["last_reviews"] == []


async def test_not_found(client: AsyncClient, sample_books):
    random_id = uuid7()

    response = await client.get(f"/api/v1/books/{random_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == f"Book with id {random_id} not found"


async def test_with_reviews_metrics(client: AsyncClient, sample_books, sample_reviews):
    target_book = sample_books[0]

    response = await client.get(f"/api/v1/books/{target_book.id}")

    assert response.status_code == 200
    data = response.json()

    assert data["reviews_qty"] == 6
    assert data["avg_rating"] == 4.5

    assert len(data["last_reviews"]) == 5

    assert data["last_reviews"][0]["user"]["full_name"] == "Test Admin Root"
    assert data["last_reviews"][0]["comment"] is not None
