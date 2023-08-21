"""Модуль работы с бд и моделями."""

from collections.abc import AsyncGenerator

from sqlalchemy import orm, select, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

import config
import schemas


engine = create_async_engine(config.DATABASE_URL)
async_session_maker = async_sessionmaker(engine)


class Base(orm.DeclarativeBase):  # noqa
    ...


metadata = Base.metadata


async def init_db():
    """Создает бд и таблицы."""
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость для получения сессии бд."""
    async with async_session_maker() as session:
        yield session


class Bet(Base):
    """Модель ставки."""

    __tablename__ = "bet"

    bet_id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    event_id: orm.Mapped[int] = orm.mapped_column(nullable=False)
    amount: orm.Mapped[float] = orm.mapped_column(nullable=False)
    state: orm.Mapped[int] = orm.mapped_column(nullable=False, default=1)


class BetDAL:
    """DAL-объект для взаимодействия со ставками."""

    def __init__(self, db_session: AsyncSession):
        """Инициализация."""
        self.db_session = db_session

    async def create(self, event_id: int, bet_amount: float) -> schemas.BetShow:
        """Создает ставку.

        Args:
            event_id: ID события.
            bet_amount: Сумма ставки.

        Returns:
            Объект созданной ставки.
        """
        new_bet = Bet(event_id=event_id, amount=bet_amount)
        self.db_session.add(new_bet)
        await self.db_session.commit()
        await self.db_session.refresh(new_bet)

        return schemas.BetShow(
            bet_id=new_bet.bet_id,
            event_id=new_bet.event_id,
            amount=new_bet.amount,
            state=new_bet.state,
        )

    async def read_all(self) -> list[schemas.BetShow]:
        """Возвращает все ставки.

        Returns:
            Последовательность всех ставок.
        """
        result = await self.db_session.execute(select(Bet))
        return [
            schemas.BetShow(
                bet_id=bet.bet_id,
                event_id=bet.event_id,
                amount=bet.amount,
                state=bet.state,
            )
            for bet in result.scalars().all()
        ]

    async def update_bet_state_by_event_id(
        self, event_ids: list[int], state: schemas.EventState
    ) -> None:
        """Обновляет статусы ставок по ID событий."""
        await self.db_session.execute(
            update(Bet)
            .where(Bet.event_id.in_(event_ids))
            .values({Bet.state: state})
            .returning(Bet)
        )
        await self.db_session.commit()
