"""Модуль с настройками и конфигурацией сервиса."""

import os

import pydantic


BET_MAKER_URL = pydantic.TypeAdapter(pydantic.HttpUrl).validate_python(
    os.getenv(key="BET_MAKER_URL", default="http://127.0.0.1:8001/")
)
