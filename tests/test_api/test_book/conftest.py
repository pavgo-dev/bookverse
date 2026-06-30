import datetime
from collections.abc import Sequence

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils.compat import uuid7

from app.dependencies import get_current_admin
from app.main import app
from app.models.book import BookOrm
from app.models.review import ReviewOrm
from app.models.user import UserOrm


@pytest.fixture(autouse=True)
def mock_admin():
    now_with_timezone = datetime.datetime.now(datetime.UTC)

    fake_admin = UserOrm(
        id=uuid7(),
        email="admin@test.com",
        hashed_password="Mocked_password_hash123",
        full_name="Test Admin Root",
        is_active=True,
        is_admin=True,
        created_at=now_with_timezone,
        updated_at=now_with_timezone,
    )

    async def mock_dependency():
        return fake_admin

    app.dependency_overrides[get_current_admin] = mock_dependency

    yield fake_admin

    if get_current_admin in app.dependency_overrides:
        del app.dependency_overrides[get_current_admin]


@pytest.fixture
async def sample_books(db_session: AsyncSession) -> Sequence[BookOrm]:
    books = [
        BookOrm(
            title="FastAPI Web Development",
            author="John Doe",
            published_year=2024,
            isbn="9781234567890",
            description="A comprehensive guide to FastAPI.",
            cover_image_url="http://example.com",
        ),
        BookOrm(
            title="Mastering Python",
            author="Jane Smith",
            published_year=2022,
            isbn="9785970601112",
            description="Deep dive into Python internals.",
            cover_image_url="http://example.com",
        ),
        BookOrm(
            title="SQLAlchemy Cookbook",
            author="John Doe",
            published_year=2025,
            isbn="9780987654321",
            description="Advanced database techniques with SQLAlchemy.",
            cover_image_url=None,
        ),
    ]

    db_session.add_all(books)
    await db_session.flush()

    return books


@pytest.fixture
async def sample_reviews(
    db_session: AsyncSession, sample_books: Sequence[BookOrm], mock_admin: UserOrm
) -> Sequence[ReviewOrm]:
    target_book = sample_books[0]
    reviews = []

    for i in range(6):
        review = ReviewOrm(
            book_id=target_book.id,
            user_id=mock_admin.id,
            user=mock_admin,
            rating=4.0 if i % 2 == 0 else 5.0,
            comment=f"Excellent book part {i}",
            created_at=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=i),
        )
        reviews.append(review)

    db_session.add_all(reviews)
    await db_session.flush()

    return reviews
