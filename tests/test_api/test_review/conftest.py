import datetime
from collections.abc import AsyncGenerator, Sequence

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils.compat import uuid7

from app.dependencies import get_current_user
from app.main import app
from app.models.book import BookOrm
from app.models.review import ReviewOrm
from app.models.user import UserOrm


@pytest.fixture
async def mock_user(db_session: AsyncSession) -> AsyncGenerator[UserOrm, None]:
    now = datetime.datetime.now(datetime.UTC)

    fake_user = UserOrm(
        id=uuid7(),
        email="user@example.com",
        hashed_password="HashedPassword123",
        full_name="Regular User",
        is_active=True,
        is_admin=False,
        created_at=now,
        updated_at=now,
    )
    db_session.add(fake_user)
    await db_session.flush()

    async def mock_dependency():
        return fake_user

    app.dependency_overrides[get_current_user] = mock_dependency

    yield fake_user

    app.dependency_overrides.clear()


@pytest.fixture
async def mock_admin(db_session: AsyncSession) -> AsyncGenerator[UserOrm, None]:
    now = datetime.datetime.now(datetime.UTC)

    fake_admin = UserOrm(
        id=uuid7(),
        email="admin@example.com",
        hashed_password="HashedPassword123",
        full_name="Admin",
        is_active=True,
        is_admin=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(fake_admin)
    await db_session.flush()

    async def mock_dependency():
        return fake_admin

    app.dependency_overrides[get_current_user] = mock_dependency

    yield fake_admin

    app.dependency_overrides.clear()


@pytest.fixture
async def sample_books(db_session: AsyncSession) -> list[BookOrm]:
    books = [
        BookOrm(
            title="FastAPI Guide",
            author="John Doe",
            published_year=2024,
            isbn="9781234567890",
            description="Test book 1 description",
            cover_image_url=None,
        ),
        BookOrm(
            title="SQLAlchemy Masterclass",
            author="Jane Smith",
            published_year=2025,
            isbn="9780987654321",
            description="Test book 2 description",
            cover_image_url=None,
        ),
    ]
    db_session.add_all(books)
    await db_session.flush()
    return books


@pytest.fixture
async def sample_review(db_session: AsyncSession, sample_books: Sequence[BookOrm], mock_user: UserOrm) -> ReviewOrm:
    target_book = sample_books[0]
    old_date = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)

    review = ReviewOrm(
        book_id=target_book.id,
        user_id=mock_user.id,
        user=mock_user,
        rating=5,
        comment="",
        created_at=old_date,
    )
    db_session.add(review)
    await db_session.flush()

    return review


@pytest.fixture
async def sample_review_2(db_session: AsyncSession, sample_books: Sequence[BookOrm]) -> ReviewOrm:
    target_book = sample_books[0]
    now = datetime.datetime.now(datetime.UTC)

    review_author = UserOrm(
        id=uuid7(),
        email="author@example.com",
        hashed_password="HashedPassword123",
        full_name="Second User",
        is_active=True,
        is_admin=False,
        created_at=now,
        updated_at=now,
    )
    db_session.add(review_author)
    await db_session.flush()

    review = ReviewOrm(
        book_id=target_book.id,
        user_id=review_author.id,
        user=review_author,
        rating=4.0,
        comment="Almost excellent book",
        created_at=now,
    )
    db_session.add(review)
    await db_session.flush()

    return review
