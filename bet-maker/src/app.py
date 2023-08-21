"""Основной модуль."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import asyncpg
import uvicorn
from fastapi import FastAPI

import db
import router
from client import http_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Обработчик событий запуска и остановки приложения."""
    # Запускаем клиентскую сессию
    http_client.start()

    # Инициализируем бд
    while True:
        try:
            await db.init_db()
        except (ConnectionRefusedError, asyncpg.exceptions.CannotConnectNowError):
            # Защита от падений в случае, если с первого раза не приконнектились
            continue
        else:
            break

    yield

    # Закрываем клиентскую сессию
    await http_client.stop()


app = FastAPI(title="bet-maker", lifespan=lifespan)

app.include_router(router.bet_router)
app.include_router(router.event_router)


@app.get("/")
async def index() -> dict[str, str]:
    """Начальная страница."""
    return {"message": "This is index page!"}


if __name__ == "__main__":
    uvicorn.run(app)
