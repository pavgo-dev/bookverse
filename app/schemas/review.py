import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateReview(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=5400, description="Book review text")
    book_id: uuid.UUID


class ReviewAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str


class ReviewResponse(CreateReview):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    user_id: uuid.UUID
    user: ReviewAuthor
