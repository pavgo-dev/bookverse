from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app import exceptions


def register_exception_handlers(app: FastAPI) -> None:

    #### СДЕЛАТЬ КОРУТИНАМИ КОГДА ДОБАВЛЮ ЛОГГЕР
    @app.exception_handler(exceptions.AppException)
    def app_exception_handler(request: Request, exception: exceptions.AppException):
        # logger.error(f"Error occurred: {str(exception)}")
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": str(exception)},
        )

    @app.exception_handler(exceptions.InvalidTokenException)
    def token_error_handler(request: Request, exception: exceptions.InvalidTokenException):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exception)},
            headers={"WWW-Authenticate": "Bearer"},
        )
