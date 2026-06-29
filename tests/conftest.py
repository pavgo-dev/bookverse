import asyncio
import sys
from collections.abc import AsyncGenerator

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import settings
from app.database import get_async_session
from app.main import app

# Настройка тестового движка БД
test_engine = create_async_engine(url=settings.TESTDATABASE_URL_psycopg, poolclass=NullPool)
test_async_session = async_sessionmaker(bind=test_engine, expire_on_commit=False, autoflush=False)


# 0. Официальный хук pytest-asyncio для Python 3.14+ (исправленный формат под mapping)
def pytest_asyncio_loop_factories():
    """Регистрирует SelectorEventLoop как именованную фабрику для тестов."""
    if sys.platform == "win32":
        import asyncio
        import selectors

        # Возвращаем СЛОВАРЬ, где ключ — любое имя, а значение — функция создания цикла
        return {"selector_loop": lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())}
    return {}


# 1. Создаю и удаляю таблицы единожды за весь запуск тестов через миграции Alembic
@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "migrations")

    # ЛЕГАЛЬНЫЙ СПОСОБ: Передаем параметры через официальный словарь attributes.
    # На это гарантированно не будут ругаться линтеры!
    alembic_cfg.attributes["test_db_url"] = settings.TESTDATABASE_URL_psycopg

    await asyncio.to_thread(command.upgrade, alembic_cfg, "head")

    yield
    await asyncio.to_thread(command.downgrade, alembic_cfg, "base")


# 2. Главная фикстура, которая держит транзакцию для всего теста
@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:

    async with (
        test_engine.connect() as connection,
        test_async_session(bind=connection) as session,
        session.begin(),
    ):
        yield session


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
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client
