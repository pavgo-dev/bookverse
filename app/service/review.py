import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserOrm


async def create_review(book_id: uuid.UUID, current_user: UserOrm, session: AsyncSession) -> ...:
    pass


async def update_review(book_id: uuid.UUID, current_user: UserOrm, session: AsyncSession) -> ...:
    pass
