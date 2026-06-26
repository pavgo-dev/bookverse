import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserOrm


async def get_user_by_id(
    session: AsyncSession, user_id: uuid.UUID | str
) -> UserOrm | None:  # str для пароля из JWT словаря
    query = select(UserOrm).where(UserOrm.id == user_id)
    result = await session.execute(query)

    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> UserOrm | None:
    query = select(UserOrm).where(UserOrm.email == email)
    result = await session.execute(query)

    return result.scalar_one_or_none()


async def get_user_by_name(session: AsyncSession, full_name: str) -> UserOrm | None:
    query = select(UserOrm).where(UserOrm.full_name == full_name)
    result = await session.execute(query)

    return result.scalar_one_or_none()
