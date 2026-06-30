from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.book import router as book_router
from app.api.v1.favorite import router as favorite_router
from app.api.v1.review import router as review_router

app = FastAPI(
    title="Bookverse API",
    description="Backend service for book catalog",
    version="0.1.0",
)


app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(book_router, prefix="/api/v1/books", tags=["Books"])
app.include_router(favorite_router, prefix="/api/v1/favorites", tags=["Favorites"])
app.include_router(review_router, prefix="/api/v1/reviews", tags=["Reviews"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Bookverse API",
        "docs_url": "/docs",
    }


# 1. Доделать tests/test_api/test_review
# 2. Рефактор, перенести БД логику из service в repository. (Может ещё DRY лишний код)
# 3. Сделать Логирование
# 4. подготовить Dockerfile и docker-compose.yml для запуска приложения вместе с PostgreSQL
#
# Дополнительно:
# 1. Реализовать refresh token и его обновление
# 2. Добавить кеширование списка книг (например, с помощью Redis) – инвалидация при добавлении/изменении книги
# 3. Добавить эндпоинт для сброса пароля через email (отправка ссылки)
# 4. Написать интеграционные тесты с реальной БД в контейнере
# 5. Добавить административную панель (например, через FastAPI admin или просто несколько админских эндпоинтов для управления пользователями)
