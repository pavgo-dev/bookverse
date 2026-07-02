from fastapi import status


class AppException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class BookNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, book_id):
        self.book_id = book_id
        super().__init__(f"The book with ID {book_id} does not exist")


class CredentialsException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self):
        super().__init__("Password or email is not correct")


class InvalidTokenException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self):
        super().__init__("Could not validate credentials")


class EmailExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, email):
        self.email = email
        super().__init__(f"User with email {email} already exists")


class NotActiveException(AppException):
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self, message: str = "Account is inactive"):
        super().__init__(message)


class ConfirmPasswordException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self):
        super().__init__("Passwords do not match")


class IsbnConflictException(AppException):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, isbn):
        self.isbn = isbn
        super().__init__(f"A book with ISBN '{isbn}' already exists")


class FavoriteExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self):
        super().__init__("This book is already in your favorites")


class FavoriteNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, book_id):
        self.book_id = book_id
        super().__init__(f"Book with ID {book_id} is not in your favorites")


class ReviewExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, book_id):
        self.book_id = book_id
        super().__init__(f"You have already left a review for book with ID {book_id}")


class ReviewNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, review_id):
        self.review_id = review_id
        super().__init__(f"Review with ID {review_id} not found")


class PermissionException(AppException):
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self):
        super().__init__("Permission denied")
