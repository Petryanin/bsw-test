"""Основной модуль."""

import uvicorn
from fastapi import FastAPI

from router import router


app = FastAPI(title="line-provider")
app.include_router(router)


@app.get("/")
async def index() -> dict[str, str]:
    """Начальная страница."""
    return {"message": "This is index page!"}


if __name__ == "__main__":
    uvicorn.run(app)
