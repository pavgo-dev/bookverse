import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import ReviewOrm
from app.models.user import UserOrm
from app.repository import book as book_repository
from app.repository import review as review_repository
from app.schemas.review import CreateReview, ReviewQueryParams, UpdateReview


async def create_review(
    book_id: uuid.UUID, review_data: CreateReview, current_user: UserOrm, session: AsyncSession
) -> ReviewOrm:
    book = await book_repository.get_book_by_id(session, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found")

    review = await review_repository.get_review(session, book_id=book_id, user_id=current_user.id)
    if review:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already left a review for this book")

    new_review = await review_repository.add_review(session, book_id, review_data, current_user)

    await session.commit()
    await session.refresh(new_review, attribute_names=["user"])

    return new_review


async def update_review(
    review_id: uuid.UUID, review_data: UpdateReview, current_user: UserOrm, session: AsyncSession
) -> ReviewOrm:
    review = await review_repository.get_review_by_id(session, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Review with id {review_id} not found")

    is_author = review.user_id == current_user.id
    if not is_author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this review"
        )

    update_data = review_data.model_dump(exclude_unset=True)
    await review_repository.update_review(session, review, update_data)

    await session.commit()
    await session.refresh(review, attribute_names=["user"])

    return review


async def get_book_reviews(query: ReviewQueryParams, book_id: uuid.UUID, session: AsyncSession) -> dict:
    book = await book_repository.get_book_by_id(session, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found")

    reviews, total = await review_repository.get_book_reviews(session, book_id, query)

    return {"total": total, "reviews": reviews}


async def delete_review(review_id: uuid.UUID, current_user: UserOrm, session: AsyncSession) -> None:
    review = await review_repository.get_review_by_id(session, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Review with id {review_id} not found")

    is_author = review.user_id == current_user.id
    is_admin = current_user.is_admin

    if not (is_author or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this review"
        )

    await review_repository.delete_review(session, review)
    await session.commit()
