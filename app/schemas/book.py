import re
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.dto.book import BookDetailDTO
from app.schemas.review import ReviewResponse


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=250)
    author: str = Field(min_length=1, max_length=150)
    published_year: int = Field(ge=0)
    isbn: str = Field(min_length=10, max_length=22)
    description: str
    cover_image_url: str | None = Field(
        default=None, max_length=500
    )  # можно использовать HttpUrl, если ссылки будут не на локальный сервер


class CreateBook(BookBase):
    @field_validator("published_year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError(f"Published year cannot be in the future. Current year is {current_year}")
        return v

    @field_validator("isbn")
    @classmethod
    def clean_and_validate_isbn(cls, v: str) -> str:
        cleaned = re.sub(r"[^0-9X]", "", v.upper())

        if len(cleaned) not in (10, 13):
            raise ValueError("ISBN is incorrect")

        return cleaned


class UpdateBook(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=250)
    author: str | None = Field(default=None, min_length=1, max_length=150)
    published_year: int | None = Field(default=None, ge=0)
    isbn: str | None = Field(default=None, min_length=10, max_length=22)
    description: str | None = None
    cover_image_url: str | None = Field(
        default=None, max_length=500
    )  # можно использовать HttpUrl, если ссылки будут не на локальный сервер

    @field_validator("published_year")
    @classmethod
    def validate_year(cls, v: int | None) -> int | None:
        if v is not None:
            current_year = datetime.now().year
            if v > current_year:
                raise ValueError(f"Published year cannot be in the future. Current year is {current_year}")
        return v

    @field_validator("isbn")
    @classmethod
    def clean_and_validate_isbn(cls, v: str | None) -> str | None:
        if v is not None:
            cleaned = re.sub(r"[^0-9X]", "", v.upper())
            if len(cleaned) not in (10, 13):
                raise ValueError("ISBN is incorrect")
            return cleaned
        return v


class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class BookListResponse(BaseModel):
    total: int = Field(description="Total number of books by specified filters")
    books: list[BookResponse]


class BookDetailResponse(BookResponse):
    avg_rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Average book rating")
    reviews_qty: int = Field(default=0, ge=0, description="Total number of reviews")
    last_reviews: list[ReviewResponse] = Field(default_factory=list, description="Top 5 latest reviews")

    @model_validator(mode="before")
    @classmethod
    def unpack_book_dto(cls, data: BookDetailDTO | dict) -> BookDetailDTO | dict:
        if isinstance(data, BookDetailDTO):
            for column in data.book.__table__.columns:
                setattr(data, column.name, getattr(data.book, column.name))

        return data


class BookQueryParams(BaseModel):
    limit: int = Field(default=10, ge=1, le=100, description="Number of books per page")
    offset: int = Field(default=0, ge=0, description="Skip the first N books")

    title: str | None = Field(default=None, description="Partial match by name")
    author: str | None = Field(default=None, description="Partial match by author")
    year_min: int | None = Field(default=None, ge=0, description="Minimum year of publication")
    year_max: int | None = Field(default=None, ge=0, le=datetime.now().year, description="Maximum year of publication")

    sort_by: Literal["title", "published_year", "author"] = Field(default="title", description="Sorting field")
    order: Literal["asc", "desc"] = Field(default="asc", description="Sorting direction")
