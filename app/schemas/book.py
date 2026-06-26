import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
