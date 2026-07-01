import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserOrm
from app.schemas.user import CreateUser


async def get_user_by_id(
    session: AsyncSession, user_id: uuid.UUID | str
) -> UserOrm | None:  # str для пароля из JWT словаря
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            return None

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


async def add_user(session: AsyncSession, user_data: CreateUser, hashed_pass: str) -> UserOrm:
    new_user = UserOrm(email=user_data.email, full_name=user_data.full_name, hashed_password=hashed_pass)
    session.add(new_user)
    await session.flush()

    return new_user


async def update_user_attributes(session: AsyncSession, current_user: UserOrm, update_data: dict) -> UserOrm:
    for key, value in update_data.items():
        setattr(current_user, key, value)
    await session.flush()
    return current_user


async def delete_user(session: AsyncSession, current_user: UserOrm) -> None:
    await session.delete(current_user)
    await session.flush()
