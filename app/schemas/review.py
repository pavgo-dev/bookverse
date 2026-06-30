import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateReview(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=5400, description="Book review text")
    # book_id: uuid.UUID   # УЖЕ ПЕРЕДАЁТСЯ Path параметром в handler если я не путаю


class ReviewAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str


class UpdateReview(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = Field(default=None, max_length=5400, description="Book review text")
    # book_id: uuid.UUID    # УЖЕ ПЕРЕДАЁТСЯ Path параметром в handler если я не путаю


class ReviewResponse(CreateReview):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    user_id: uuid.UUID
    user: ReviewAuthor


class ReviewQueryParams(BaseModel):
    limit: int = Field(default=10, ge=1, le=100, description="Number of reviews per page")
    offset: int = Field(default=0, ge=0, description="Skip the first N reviews")


class ReviewListResponse(BaseModel):
    total: int = Field(description="Total number of reviews")
    reviews: list[ReviewResponse]
