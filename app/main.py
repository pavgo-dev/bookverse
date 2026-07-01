from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.book import router as book_router
from app.api.v1.favorite import router as favorite_router
from app.api.v1.review import router as review_router

app = FastAPI(
    title="Bookverse API",
    description="Backend service for book catalog",
    version="0.1.0",
)

# Настраиваем список разрешенных адресов.
# Сюда нужно вписать адрес, на котором будет работать сайт (фронтенд)
origins = [
    "http://localhost:3000",  # Стандартный порт для React / Next.js
    "http://localhost:5173",  # Стандартный порт для Vite / Vue
    "http://127.0.0.1:3000",
]

# Подключаем CORS к приложению
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешаем запросы только с этих адресов
    allow_credentials=True,  # Разрешаем передачу кук и JWT-токенов в headers
    allow_methods=["*"],  # Разрешаем любые методы (GET, POST, PUT, PATCH, DELETE)
    allow_headers=["*"],  # Разрешаем любые заголовки
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
# 4. Добавить административную панель (например, через FastAPI admin или просто несколько админских эндпоинтов для управления пользователями)
