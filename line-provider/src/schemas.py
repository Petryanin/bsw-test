"""Описания типов данных, используемых для запросов/ответов."""


import decimal
import enum
import time
from http import HTTPStatus

from fastapi import HTTPException
from pydantic import BaseModel, field_validator


@enum.unique
class EventState(enum.IntEnum):
    """Перечисление статусов событий."""

    DELETED = 0
    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3


class EventCreate(BaseModel):
    """Схема создаваемого события."""

    coefficient: decimal.Decimal | None = None
    deadline: int | None = None

    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, value: int | None) -> int | None:
        """Валидация дедлайна.

        Args:
            value: Значение валидируемого параметра.

        Raises:
            HTTPException: Если введенный дедлайн уже прошел.

        Returns:
            Приведенный дедлайн или None, если он не объявлен.
        """
        if value is not None and value < time.time():
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail="The deadline has already passed!",
            )

        return int(value) if value is not None else value

    @field_validator("coefficient")
    @classmethod
    def validate_coefficient(
        cls, value: decimal.Decimal | None
    ) -> decimal.Decimal | None:
        """Валидация коэффициента события.

        Args:
            value: Значение валидируемого параметра.

        Raises:
            HTTPException: Если коэффициент <= 0.

        Returns:
            Приведенный коэффициент или None, если он не объявлен.
        """
        if value is not None and value <= 0:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail="The coefficient must be greater than zero!",
            )

        return round(value, 2) if value is not None else value


class Event(EventCreate):
    """Схема события."""

    event_id: int
    state: EventState
