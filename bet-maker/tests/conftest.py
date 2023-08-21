"""Конфигурация для тестов."""

import asyncio
from collections.abc import AsyncGenerator, Generator

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.client import http_client
from src import app, config, db


engine_test = create_async_engine(config.DATABASE_URL)
async_session_maker = async_sessionmaker(engine_test)

db.metadata.bind = engine_test


async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Переопределенная зависимость для получения сессии бд."""
    async with async_session_maker() as session:
        yield session


async def override_get_async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Переопределенная зависимость для получения сессии клиента."""
    async with httpx.AsyncClient() as ac:
        yield ac


@pytest.fixture(autouse=True, scope="session")
def dependencies() -> Generator[None, None, None]:
    """Фикстура переопределения зависимостей."""
    app.app.dependency_overrides[db.get_session] = override_get_db_session
    app.app.dependency_overrides[http_client] = override_get_async_client

    yield

    app.app.dependency_overrides = {}


@pytest.fixture(autouse=True, scope="session")
async def database() -> AsyncGenerator[None, None]:
    """Фикстура создания и удаления бд."""
    async with engine_test.begin() as conn:
        await conn.run_sync(db.metadata.create_all)

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(db.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Фикстура создания экземляра событийного цикла для каждого теста."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Фикстура получения сессии клиента."""
    async with httpx.AsyncClient(
        app=app.app, base_url="http://127.0.0.1:8001"
    ) as session:
        yield session
