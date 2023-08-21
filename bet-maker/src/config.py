"""Модуль с настройками и конфигурацией сервиса."""

import os

import pydantic


DATABASE_URL = os.getenv(
    key="DATABASE_URL",
    default="postgresql+asyncpg://postgres:password@127.0.0.1:5432/prod",
)

LINE_PROVIDER_URL = pydantic.TypeAdapter(pydantic.HttpUrl).validate_python(
    os.getenv(key="LINE_PROVIDER_URL", default="http://127.0.0.1:8002/")
)
