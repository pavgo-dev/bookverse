from httpx import AsyncClient
from uuid_utils.compat import uuid7


async def test_succes(client: AsyncClient, sample_books, sample_review, sample_review_2):
    book = sample_books[0]
    params = {"limit": 10, "offset": 0}

    response = await client.get(f"/api/v1/reviews/{book.id}", params=params)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 2

    assert "id" in data["reviews"][0]
    assert "id" in data["reviews"][1]

    assert "user_id" in data["reviews"][0]
    assert "user_id" in data["reviews"][1]

    assert "created_at" in data["reviews"][0]
    assert "created_at" in data["reviews"][1]

    assert data["reviews"][0]["rating"] == 4
    assert data["reviews"][1]["rating"] == 5

    assert data["reviews"][0]["comment"] == "Almost excellent book"
    assert data["reviews"][1]["comment"] == ""

    assert data["reviews"][0]["user"] == {"full_name": "Second User"}
    assert data["reviews"][1]["user"] == {"full_name": "Regular User"}


async def test_limit(client: AsyncClient, sample_books, sample_review, sample_review_2):
    book = sample_books[0]
    params = {"limit": 1, "offset": 0}

    response = await client.get(f"/api/v1/reviews/{book.id}", params=params)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 2
    assert len(data["reviews"]) == 1

    # Вернулся именно первый по дате коммент
    assert data["reviews"][0]["comment"] == "Almost excellent book"


async def test_offset(client: AsyncClient, sample_books, sample_review, sample_review_2):
    book = sample_books[0]
    params = {"limit": 10, "offset": 1}

    response = await client.get(f"/api/v1/reviews/{book.id}", params=params)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 2
    assert len(data["reviews"]) == 1

    # Вернулся второй, первый пропустил
    assert data["reviews"][0]["comment"] == ""


async def test_book_not_found(client: AsyncClient, sample_books, sample_review, sample_review_2):
    random_id = uuid7()
    params = {"limit": 10, "offset": 0}

    response = await client.get(f"/api/v1/reviews/{random_id}", params=params)

    assert response.status_code == 404
