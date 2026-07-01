import pytest
from httpx import AsyncClient
from uuid_utils.compat import uuid7

review_data = {
    "rating": 4,
    "comment": "This is test comment",
}


async def test_succes(client: AsyncClient, mock_user, sample_books):
    target_book = sample_books[0]

    response = await client.post(f"/api/v1/reviews/{target_book.id}", json=review_data)

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data
    assert data["rating"] == 4
    assert data["comment"] == "This is test comment"
    assert data["user"] == {"full_name": "Regular User"}


async def test_no_authorization(client: AsyncClient, sample_books):
    target_book = sample_books[0]

    response = await client.post(f"/api/v1/reviews/{target_book.id}", json=review_data)

    assert response.status_code == 401


async def test_review_exists(client: AsyncClient, mock_user, sample_books, sample_review):
    target_book = sample_books[0]

    response = await client.post(f"/api/v1/reviews/{target_book.id}", json=review_data)

    assert response.status_code == 409


async def test_book_not_found(client: AsyncClient, mock_user):
    random_id = uuid7()
    response = await client.post(f"/api/v1/reviews/{random_id}", json=review_data)

    assert response.status_code == 404


@pytest.mark.parametrize(
    "points",
    [10, 0, 0.8],
)
async def test_incorrect_rating(client: AsyncClient, mock_user, sample_books, points):
    target_book = sample_books[0]
    review_data = {
        "rating": points,
        "comment": "This is test comment",
    }

    response = await client.post(f"/api/v1/reviews/{target_book.id}", json=review_data)

    assert response.status_code == 422
