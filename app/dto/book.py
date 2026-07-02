from collections.abc import Sequence
from dataclasses import dataclass

from app.models.book import BookOrm
from app.models.review import ReviewOrm


@dataclass
class BookDetailDTO:
    book: BookOrm
    avg_rating: float
    reviews_qty: int
    last_reviews: Sequence[ReviewOrm]
