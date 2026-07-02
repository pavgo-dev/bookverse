from datetime import UTC, datetime, timedelta
from typing import Literal

import jwt
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app import exceptions
from app.config import settings
from app.database import get_async_session
from app.models.user import UserOrm
from app.repository import user as user_repository
from app.schemas.book import BookQueryParams

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> UserOrm:

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str | None = payload.get("sub")

        if user_id is None:
            raise exceptions.InvalidTokenException()

    except jwt.PyJWTError:
        raise exceptions.InvalidTokenException() from None

    user = await user_repository.get_user_by_id(session, user_id)

    if user is None:
        raise exceptions.InvalidTokenException()

    if not user.is_active:
        raise exceptions.NotActiveException()

    return user


async def get_current_admin(
    current_user: UserOrm = Depends(get_current_user),
) -> UserOrm:

    if not current_user.is_admin:
        raise exceptions.PermissionException
    return current_user
