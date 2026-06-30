import datetime
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils.compat import uuid7

from app.dependencies import get_current_user
from app.main import app
from app.models.book import BookOrm
from app.models.user import UserOrm


@pytest.fixture(autouse=True)
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

    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]


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
