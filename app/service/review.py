import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import ReviewOrm
from app.models.user import UserOrm
from app.repository import review as review_repository
from app.schemas.review import CreateReview, ReviewQueryParams, UpdateReview


async def create_review(
    book_id: uuid.UUID, review_data: CreateReview, current_user: UserOrm, session: AsyncSession
) -> ReviewOrm:
    review = await review_repository.get_review(session, book_id=book_id, user_id=current_user.id)
    if review:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already left a review for this book")

    new_review = ReviewOrm(
        user_id=current_user.id, book_id=book_id, rating=review_data.rating, comment=review_data.comment
    )

    session.add(new_review)
    await session.commit()
    await session.refresh(new_review, attribute_names=["user"])

    return new_review


async def update_review(
    review_id: uuid.UUID, review_data: UpdateReview, current_user: UserOrm, session: AsyncSession
) -> ReviewOrm:
    review = await review_repository.get_review_by_id(session, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review is not found")

    is_author = review.user_id == current_user.id
    if not is_author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this review"
        )

    update_data = review_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(review, key, value)

    await session.commit()
    await session.refresh(review)

    return review


async def get_book_reviews(query: ReviewQueryParams, book_id: uuid.UUID, session: AsyncSession) -> dict:
    reviews, total = await review_repository.get_book_reviews(session, book_id, query)

    return {"total": total, "reviews": reviews}


async def delete_review(review_id: uuid.UUID, current_user: UserOrm, session: AsyncSession) -> None:
    review = await review_repository.get_review_by_id(session, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review is not found")

    is_author = review.user_id == current_user.id
    is_admin = current_user.is_admin

    if not (is_author or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this review"
        )

    await session.delete(review)
    await session.commit()
