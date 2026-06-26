import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreateFavorite(BaseModel):
    book_id: uuid.UUID


class FavoriteResponse(CreateFavorite):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    added_at: datetime
