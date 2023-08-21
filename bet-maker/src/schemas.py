"""Описания типов данных, используемых для запросов/ответов."""

import decimal
import enum
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


class EventShow(BaseModel):
    """Публичная схема события."""

    event_id: int
    coefficient: decimal.Decimal | None = None
    deadline: int | None = None
    state: EventState


class BetCreate(BaseModel):
    """Схема создаваемой ставки."""

    event_id: int
    amount: float

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: float) -> float:
        """Валидация суммы ставки.

        Args:
            value: Значение валидируемого параметра.

        Raises:
            HTTPException: Если сумма <= 0.

        Returns:
            Приведенная сумма.
        """
        if value <= 0:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail="The bet amount must be greater than zero!",
            )

        return round(value, 2)


class BetShow(BaseModel):
    """Публичная схема ставки."""

    bet_id: int
    event_id: int
    amount: float
    state: int
