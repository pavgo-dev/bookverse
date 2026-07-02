from fastapi import status
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: str = Field(..., examples=["An error occurred on the server"])


class CredentialsErrorResponse(ErrorResponse):
    detail: str = Field("Password or email is not correct", examples=["Password or email is not correct"])


class EmailExistsErrorResponse(ErrorResponse):
    detail: str = Field("User with email already exists", examples=["User with user@example.com already exists"])


class NotActiveErrorResponse(ErrorResponse):
    detail: str = Field(
        "Account is inactive", examples=["Account is inactive", "Account is suspended", "Email confirmation required"]
    )


class ConfirmPasswordErrorResponse(ErrorResponse):
    detail: str = Field("Passwords do not match", examples=["Passwords do not match"])


class TokenErrorResponse(ErrorResponse):
    detail: str = Field("Could not validate credentials", examples=["Could not validate credentials"])


class BookNotFoundErrorResponse(ErrorResponse):
    detail: str = Field(
        "The book with ID ... does not exist",
        examples=["The book with ID 01907293-68d0-7ec3-8df8-d633036c84cc does not exist"],
    )


class IsbnConflictErrorResponse(ErrorResponse):
    detail: str = Field(
        "A book with ISBN '...' already exists", examples=["A book with ISBN '978-3-16-148410-0' already exists"]
    )


class PermissionErrorResponse(ErrorResponse):
    detail: str = Field("Permission denied", examples=["Permission denied"])


class FavoriteExistsErrorResponse(ErrorResponse):
    detail: str = Field("This book is already in your favorites", examples=["This book is already in your favorites"])


class FavoriteNotFoundErrorResponse(ErrorResponse):
    detail: str = Field(
        "Book with ID ... is not in your favorites",
        examples=["Book with ID 01907293-68d0-7ec3-8df8-d633036c84cc is not in your favorites"],
    )


class ReviewExistsErrorResponse(ErrorResponse):
    detail: str = Field(
        "You have already left a review for book with ID ...",
        examples=["You have already left a review for book with ID 01907293-68d0-7ec3-8df8-d633036c84cc"],
    )


class ReviewNotFoundErrorResponse(ErrorResponse):
    detail: str = Field(
        "Review with ID ... not found", examples=["Review with ID 01907293-68d0-7ec3-8df8-d633036c84cc not found"]
    )


CURRENT_USER_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": TokenErrorResponse,
        "description": "Token missing, expired, or user not found in database",
    },
    status.HTTP_403_FORBIDDEN: {
        "model": NotActiveErrorResponse,
        "description": "User account is inactive, suspended, or disabled",
    },
}

ADMIN_RESPONSES = {
    **CURRENT_USER_RESPONSES,
    status.HTTP_403_FORBIDDEN: {
        "model": PermissionErrorResponse,
        "description": "Access denied. Only superusers can perform this action",
    },
}
