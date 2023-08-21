"""Модуль с роутерами."""

from http import HTTPStatus

import httpx
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import Json
from sqlalchemy.ext import asyncio

import db
import ext
import schemas
from client import http_client

bet_router = APIRouter(tags=["bet"])
event_router = APIRouter(tags=["event"])


@event_router.get("/events")
async def get_events(
    client_session: httpx.AsyncClient = Depends(http_client),
) -> list[schemas.EventShow]:
    """Возвращает список событий, на которые можно совершить ставку,
    от сервиса `line-provider`.
    \f
    Args:
        client_session: Клиентская сессия.

    Returns:
        Список подходящих событий.
    """
    return await ext.get_events_from_line_provider(client_session)


@event_router.post("/updated")
async def receive_updated_event_info(
    events: Json = Body(),
    db_session: asyncio.AsyncSession = Depends(db.get_session),
) -> None:
    """Обрабатывает информацию об обновленных статусах событий
    от сервиса `line-provider`.

    Выставляет соответствующие статусы на ставках.
    \f
    Args:
        db_session: Сессия бд.
    """
    event_list = list(events.values())
    await db.BetDAL(db_session).update_bet_state_by_event_id(
        event_ids=[event["event_id"] for event in event_list],
        state=event_list[0]["state"],
    )


@bet_router.post("/bet")
async def make_bet(
    bet: schemas.BetCreate,
    client_session: httpx.AsyncClient = Depends(http_client),
    db_session: asyncio.AsyncSession = Depends(db.get_session),
) -> schemas.BetShow:
    """Сделать ставку на событие.
    \f
    Args:
        bet: Объект создаваемой ставки.
        client_session: Клиентская сессия.
        db_session: Сессия бд.

    Returns:
        Объект созданной ставки.
    """
    events = await ext.get_events_from_line_provider(client_session)
    if not events or bet.event_id not in {_["event_id"] for _ in events}:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Event not found!")

    return await db.BetDAL(db_session).create(bet.event_id, bet.amount)


@bet_router.get("/bets")
async def get_all_bets(
    db_session: asyncio.AsyncSession = Depends(db.get_session),
) -> list[schemas.BetShow]:
    """Возвращает список всех сделанных ставок.
    \f
    Args:
        db_session: Сессия бд.

    Returns:
        Список ставок.
    """
    return await db.BetDAL(db_session).read_all()
