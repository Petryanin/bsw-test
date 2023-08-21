"""Модуль с конфигурацией клиента."""

import httpx


class HttpClient:
    """Клиентская модель для взаимодействия с внешними сервисами."""

    session: httpx.AsyncClient | None = None

    def start(self) -> None:
        """Открывает клиентскую сессию."""
        self.session = httpx.AsyncClient()

    async def stop(self) -> None:
        """Закрывает клиентскую сессию."""
        if self.session is not None:
            await self.session.aclose()
            self.session = None

    def __call__(self) -> httpx.AsyncClient:
        """Возвращает клиентскую сессию."""
        if self.session is None:
            self.start()
        assert self.session is not None
        return self.session


http_client = HttpClient()
