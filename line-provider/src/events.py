"""Хранилище событий."""

import decimal
import random
import time

import schemas


MIN_COEFFICIENT = 0.01
MAX_COEFFICIENT = 10.0


events: dict[int, schemas.Event] = {}
secure_random = random.SystemRandom()


def generate(number: int = 1) -> dict[int, schemas.Event]:
    """Генерирует события в переданном количестве и сохраняет их в хранилище.

    Args:
        number: Количество событий.

    Returns:
        Сгенерированные события.
    """
    generated_events = {}

    for i in range(1, number + 1):
        timestamp = time.time()

        event = schemas.Event(
            event_id=max(events or [0]) + i,
            coefficient=round(
                decimal.Decimal(
                    secure_random.uniform(MIN_COEFFICIENT, MAX_COEFFICIENT)
                ),
                2,
            ),
            deadline=int(secure_random.uniform(timestamp + 30, timestamp + 600)),
            state=schemas.EventState.NEW,
        )

        generated_events[event.event_id] = event

    events.update(generated_events)

    return generated_events
