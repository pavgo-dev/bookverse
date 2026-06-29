from datetime import UTC, datetime, timedelta
from typing import Literal

import jwt
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

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

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str | None = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except jwt.PyJWTError:
        raise credentials_exception from None

    user = await user_repository.get_user_by_id(session, user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is banned")

    return user


async def get_current_admin(
    current_user: UserOrm = Depends(get_current_user),
) -> UserOrm:

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    return current_user


def get_book_query_params(
    limit: int = Query(default=10, ge=1, le=100, description="Number of books per page"),
    offset: int = Query(default=0, ge=0, description="Skip the first N books"),
    title: str | None = Query(default=None, description="Partial match by name"),
    author: str | None = Query(default=None, description="Partial match by author"),
    year_min: int | None = Query(default=None, ge=0, description="Minimum year of publication"),
    year_max: int | None = Query(default=None, ge=0, description="Maximum year of publication"),
    sort_by: Literal["title", "published_year", "author"] = Query(
        default="title", description="Sorting field (title, published_year, author)"
    ),
    order: Literal["asc", "desc"] = Query(default="asc", description="Sorting direction (asc, desc)"),
) -> BookQueryParams:

    return BookQueryParams(
        limit=limit,
        offset=offset,
        title=title,
        author=author,
        year_min=year_min,
        year_max=year_max,
        sort_by=sort_by,
        order=order,
    )
