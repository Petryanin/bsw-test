"""Модуль взаимодействия с внешними сервисами."""

import httpx

import config


async def send_event_update(payload: str) -> None:
    """Отправляет уведомление в сервис `bet-maker` об обноволенном событии.

    Args:
        payload: JSON-объект с отправляемыми данными.
    """
    async with httpx.AsyncClient() as session:
        await session.post(f"{config.BET_MAKER_URL}updated", json=payload)
