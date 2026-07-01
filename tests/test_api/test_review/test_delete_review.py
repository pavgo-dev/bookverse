from httpx import AsyncClient
from uuid_utils.compat import uuid7

from app.dependencies import get_current_user
from app.main import app


async def test_succes_user(client: AsyncClient, mock_user, sample_review):
    response = await client.delete(f"/api/v1/reviews/{sample_review.id}")

    assert response.status_code == 204


async def test_succes_admin(client: AsyncClient, mock_admin, sample_review_2):
    response = await client.delete(f"/api/v1/reviews/{sample_review_2.id}")

    assert response.status_code == 204


async def test_no_authorization(client: AsyncClient, sample_review):
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]

    response = await client.delete(f"/api/v1/reviews/{sample_review.id}")

    assert response.status_code == 401


async def test_review_not_found(client: AsyncClient, mock_user, sample_review):
    random_id = uuid7()
    response = await client.delete(f"/api/v1/reviews/{random_id}")

    assert response.status_code == 404


async def test_no_author_or_admin(client: AsyncClient, mock_user, sample_review_2):
    response = await client.delete(f"/api/v1/reviews/{sample_review_2.id}")

    assert response.status_code == 403
