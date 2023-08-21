"""Модуль взаимодействия с внешними сервисами."""

import httpx

import config
import schemas


async def get_events_from_line_provider(
    client_session: httpx.AsyncClient,
) -> list[schemas.EventShow]:
    """Возвращает список событий, на которые можно совершить ставку,
    от сервиса `line-provider`.

    Args:
        client_session: Клиентская сессия.

    Returns:
        Список подходящих событий.
    """
    response = await client_session.get(f"{config.LINE_PROVIDER_URL}event/new")
    return response.json()
