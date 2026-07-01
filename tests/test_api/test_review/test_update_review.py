import pytest
from httpx import AsyncClient
from uuid_utils.compat import uuid7

update_data = {
    "rating": 3,
    "comment": "I changed my mind",
}


async def test_success(client: AsyncClient, mock_user, sample_review):
    response = await client.patch(f"/api/v1/reviews/{sample_review.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()

    assert data["rating"] == 3
    assert data["comment"] == "I changed my mind"
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data
    assert data["user"] == {"full_name": "Regular User"}


async def test_success_rating(client: AsyncClient, mock_user, sample_review):
    response = await client.patch(f"/api/v1/reviews/{sample_review.id}", json={"rating": 4})

    assert response.status_code == 200
    data = response.json()

    assert data["rating"] == 4
    assert data["comment"] == ""
    assert data["user"] == {"full_name": "Regular User"}


async def test_success_data(client: AsyncClient, mock_user, sample_review):
    response = await client.patch(f"/api/v1/reviews/{sample_review.id}", json={"comment": "Brand new review"})

    assert response.status_code == 200
    data = response.json()

    assert data["rating"] == 5
    assert data["comment"] == "Brand new review"
    assert data["user"] == {"full_name": "Regular User"}


async def test_no_authorization(client: AsyncClient, sample_review_2):
    response = await client.patch(f"/api/v1/reviews/{sample_review_2.id}", json=update_data)

    assert response.status_code == 401


async def test_update_foreign_review(client: AsyncClient, mock_user, sample_review_2):
    response = await client.patch(f"/api/v1/reviews/{sample_review_2.id}", json=update_data)

    assert response.status_code == 403


async def test_not_found(client: AsyncClient, mock_user):
    random_id = uuid7()
    response = await client.patch(f"/api/v1/reviews/{random_id}", json=update_data)

    assert response.status_code == 404


@pytest.mark.parametrize("points", [10, 3.5, 0])
async def test_update_incorrect_rating(client: AsyncClient, mock_user, sample_review, points):
    response = await client.patch(f"/api/v1/reviews/{sample_review.id}", json={"rating": points, "comment": ""})

    assert response.status_code == 422
