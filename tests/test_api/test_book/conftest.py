from collections.abc import Sequence

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import BookOrm


@pytest.fixture
async def sample_books(db_session: AsyncSession) -> Sequence[BookOrm]:
    books = [
        BookOrm(
            title="FastAPI Web Development",
            author="John Doe",
            published_year=2024,
            isbn="978-1-23456-789-0",
            description="A comprehensive guide to FastAPI.",
            cover_image_url="http://example.com",
        ),
        BookOrm(
            title="Mastering Python",
            author="Jane Smith",
            published_year=2022,
            isbn="978-5-97060-111-2",
            description="Deep dive into Python internals.",
            cover_image_url="http://example.com",
        ),
        BookOrm(
            title="SQLAlchemy Cookbook",
            author="John Doe",
            published_year=2025,
            isbn="978-0-98765-432-1",
            description="Advanced database techniques with SQLAlchemy.",
            cover_image_url=None,
        ),
    ]

    db_session.add_all(books)
    await db_session.flush()

    return books
