import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.book import BookResponse


class CreateFavorite(BaseModel):
    book_id: uuid.UUID


class FavoriteResponse(CreateFavorite):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    added_at: datetime


class FavoriteQueryParams(BaseModel):
    limit: int = Field(default=10, ge=1, le=100, description="Number of books per page")
    offset: int = Field(default=0, ge=0, description="Skip the first N books")


class FavoriteListResponse(BaseModel):
    total: int = Field(description="Total number of favorite books")
    books: list[BookResponse]
