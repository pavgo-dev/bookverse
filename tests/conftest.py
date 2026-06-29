from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database import Base, get_async_session
from app.main import app

# Настройка тестового движка БД
test_engine = create_async_engine(url=settings.TESTDATABASE_URL_psycopg)
test_async_session = async_sessionmaker(bind=test_engine, expire_on_commit=False, autoflush=False)


# 1. Создаю и удаляею таблицы единожды за весь запуск тестов
@pytest.fixture(scope="session", autouse=True)  # scope="session" ЗАПУСКАЕТ ОДИН РАЗ ПЕРЕД СЕССИЕЙ ТЕСТОВ
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# 2. Главная фикстура, которая держит транзакцию для всего теста
@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:

    async with (
        test_engine.connect() as connection,
        test_async_session(bind=connection) as session,
        session.begin(),  # Запускаем транзакцию. Переменная 'as transaction' больше не нужна!
    ):
        yield session
        # Вызывать rollback вручную здесь НЕ НАДО.
        # Context manager 'session.begin()' сам сделает ROLLBACK при выходе из блока,
        # так как мы не вызвали 'await session.commit()'.


# 3. Переопределить зависимость FastAPI, используя ту же фикстуру db_session
@pytest.fixture(autouse=True)
async def override_dependency(db_session: AsyncSession):
    async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_async_session] = get_test_session
    yield
    app.dependency_overrides.clear()


# 4. АСИНХРОННЫЙ клиент для отправки HTTP-запросов к FastAPI
@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    # Используем ASGITransport для прямого вызова приложения без запуска реального сервера
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
