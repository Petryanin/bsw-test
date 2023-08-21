"""Модуль тестов API."""

# flake8: noqa

import json
from http import HTTPStatus

from httpx import AsyncClient

from src import config


async def test_get_events(ac: AsyncClient):
    response = await ac.post(
        "/updated",
        json=json.dumps(
            {
                "1": {
                    "coefficient": "7.96",
                    "deadline": 1692749643,
                    "event_id": 1,
                    "state": 1,
                }
            }
        ),
    )

    assert response.status_code == HTTPStatus.OK


async def test_receive_updated_event_info(ac: AsyncClient):
    response = await ac.get("/events")

    assert response.status_code == HTTPStatus.OK


async def test_get_bets(ac: AsyncClient):
    response = await ac.get("/bets")

    assert response.status_code == HTTPStatus.OK


async def test_make_bet(ac: AsyncClient):
    async with AsyncClient() as session:
        response = await session.post(f"{config.LINE_PROVIDER_URL}event/generate/1")

    new_event_id = response.json()[0]["event_id"]
    bet = {"event_id": new_event_id, "amount": 1}

    response = await ac.post("/bet", json=bet)

    assert response.status_code == HTTPStatus.OK
