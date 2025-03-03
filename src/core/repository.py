from typing import Any, Type, TypeVar

from sqlalchemy import delete, exists, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

T = TypeVar("T", bound=SQLModel)


class SQLModelRepository:
    """Base repository class for SQLModel entities"""

    model: Type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> T:
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def get(self, id: Any) -> T | None:
        obj = await self.session.execute(select(self.model).where(self.model.id == id))
        return obj.scalar_one_or_none()

    async def all(self) -> list[T]:
        obj = await self.session.execute(select(self.model))
        return obj.scalars().all()

    async def delete(self, id: Any) -> bool:
        obj = await self.session.execute(
            delete(self.model).where(self.model.id == id).returning(self.model.id)
        )
        await self.session.flush()
        return obj.scalar_one_or_none() is not None

    async def update(self, id: Any, data: dict) -> T | None:
        obj = await self.session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**data)
            .returning(self.model)
        )
        await self.session.flush()
        return obj.scalar_one_or_none()

    async def filter(self, **kwargs: dict[str, Any]) -> list[T]:
        conditions = [
            getattr(self.model, key) == value for key, value in kwargs.items()
        ]
        obj = await self.session.execute(select(self.model).where(*conditions))
        return obj.scalars().all()

    async def count(self) -> int:
        obj = await self.session.execute(select(func.count()).select_from(self.model))
        return obj.scalar_one()

    async def exists(self, id: Any) -> bool:
        obj = await self.session.execute(select(exists().where(self.model.id == id)))
        return obj.scalar_one()
