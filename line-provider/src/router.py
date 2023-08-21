"""Модуль с роутерами."""

import decimal
import json
import time
from http import HTTPStatus

from fastapi import APIRouter, HTTPException

import ext
import schemas
from events import events, generate


router = APIRouter(prefix="/event", tags=["event"])
update_callback_router = APIRouter()


@router.get("/new")
async def get_new_events() -> list[schemas.Event]:
    """Возвращает список событий, на которые можно совершить ставку.

    Таковыми считаются все события, для которых ещё не наступил дедлайн для ставок.
    """
    return [
        event
        for event in events.values()
        if event.deadline and int(time.time()) < event.deadline
    ]


@router.get("/all")
async def get_all_events() -> list[schemas.Event]:
    """Возвращает список всех событий."""
    return list(events.values())


@router.get("/{event_id}")
async def get_event(event_id: int) -> schemas.Event:
    """Возвращает событие по его ID.
    \f
    Args:
        event_id: ID события.

    Raises:
        HTTPException: Если событие с данным ID не найдено.

    Returns:
        Объект события.
    """
    if event_id not in events:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Event not found!")

    return events[event_id]


@router.post("/generate/{number}")
async def generate_events(number: int) -> list[schemas.Event]:
    """Возвращает список сгенерированных событий по переданному количеству.
    \f
    Args:
        number: Количество событий, которое необходимо сгенерировать.

    Returns:
        Список событий.
    """
    return list(generate(number).values())


@router.post("/create")
async def create_event(event: schemas.EventCreate) -> schemas.Event:
    """Создает событие.
    \f
    Args:
        event: Объект события.

    Returns:
        Объект созданного события.
    """
    event_id = max(events or [0]) + 1

    events[event_id] = schemas.Event(
        event_id=event_id,
        coefficient=event.coefficient or round(decimal.Decimal(1), 2),
        deadline=event.deadline or int(time.time()) + 3600,
        state=schemas.EventState.NEW,
    )

    return events[event_id]


@router.put("/update")
async def update_event(event: schemas.Event) -> schemas.Event:
    """Обновляет событие.

    Если изменился статус события, уведомляет об этом сервис ставок `bet-maker`
    \f
    Args:
        event: Объект события.

    Returns:
        Объект измененного события.
    """
    if event.event_id not in events:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Event not found!")

    if event.state not in {1, 2, 3}:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="There is no such event state!",
        )

    is_state_changed = event.state is not events[event.event_id].state

    for p_name, p_value in event.model_dump(exclude_unset=True).items():
        setattr(events[event.event_id], p_name, p_value)

    if is_state_changed:
        await ext.send_event_update(
            json.dumps({event.event_id: event.model_dump()}, default=float)
        )

    return events[event.event_id]


@router.delete("/delete/all")
async def delete_all_events() -> dict:
    """Удаляет все события.

    Уведомляет об этом сервис ставок `bet-maker`.
    """
    if not events:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="There are no events!"
        )

    for _, event in events.items():
        event.state = schemas.EventState.DELETED

    await ext.send_event_update(
        json.dumps(
            {event.event_id: event.model_dump() for event in events.values()},
            default=float,
        )
    )

    events.clear()

    return {"result": True, "message": "All events were successfully deleted!"}


@router.delete("/delete/{event_id}")
async def delete_event(event_id: int) -> dict:
    """Удаляет событие по переданному ID.

    Уведомляет об этом сервис ставок `bet-maker`.
    \f
    Args:
        event_id: Объект события.

    Returns:
        Объект результата.
    """
    if event_id not in events:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Event not found!")

    events[event_id].state = schemas.EventState.DELETED

    await ext.send_event_update(
        json.dumps({event_id: events[event_id].model_dump()}, default=int)
    )

    del events[event_id]

    return {"result": True, "message": f"Event {event_id} was successfully deleted!"}
