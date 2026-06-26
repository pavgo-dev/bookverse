import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Annotated

from sqlalchemy import UUID, DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column
from uuid_utils.compat import uuid7

from app.config import settings


class Base(DeclarativeBase):
    pass


uuid_pk = Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), default=uuid7, primary_key=True)]
uuid_fk = Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True))]
time_mark = Annotated[datetime, mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)]
update_time_mark = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    ),
]


async_engine = create_async_engine(url=settings.DATABASE_URL_psycopg_async, echo=False)
async_session_factory = async_sessionmaker(bind=async_engine, expire_on_commit=False, autoflush=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
