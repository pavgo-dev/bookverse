from httpx import AsyncClient
from uuid_utils.compat import uuid7


async def test_update_book_partial_success(client: AsyncClient, sample_books):
    target_book = sample_books[0]
    update_data = {"title": "Super New FastAPI Title", "published_year": 2025}

    response = await client.patch(f"/api/v1/books/{target_book.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == update_data["title"]
    assert data["published_year"] == update_data["published_year"]
    assert data["author"] == target_book.author


async def test_update_book_with_isbn_cleaning_success(client: AsyncClient, sample_books):
    target_book = sample_books[0]
    update_data = {"isbn": "978-5-97060-999-9"}

    response = await client.patch(f"/api/v1/books/{target_book.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()

    assert data["isbn"] == "9785970609999"


async def test_update_book_not_found(client: AsyncClient, sample_books):
    random_id = uuid7()
    update_data = {"title": "New Title"}

    response = await client.patch(f"/api/v1/books/{random_id}", json=update_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


async def test_update_book_isbn_conflict(client: AsyncClient, sample_books):
    book_to_update = sample_books[0]
    other_book = sample_books[1]

    update_data = {"isbn": other_book.isbn}

    response = await client.patch(f"/api/v1/books/{book_to_update.id}", json=update_data)

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


async def test_update_book_self_isbn(client: AsyncClient, sample_books):
    target_book = sample_books[0]
    update_data = {
        "title": "Just updated title",
        "isbn": target_book.isbn,
    }

    response = await client.patch(f"/api/v1/books/{target_book.id}", json=update_data)

    assert response.status_code == 200
    assert response.json()["title"] == update_data["title"]
