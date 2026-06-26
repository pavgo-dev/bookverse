from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.book import router as book_router

app = FastAPI(
    title="Bookverse API",
    description="Backend service for book catalog",
    version="0.1.0",
)


app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(book_router, prefix="/api/v1/books", tags=["Books"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Bookverse API!",
        "docs_url": "/docs",
    }
