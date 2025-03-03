from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar

from sqlalchemy import delete, exists, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

T = TypeVar("T", bound=SQLModel)


class GenericRepository(Generic[T], ABC):
    @abstractmethod
    async def create(self, data: T) -> T: ...

    @abstractmethod
    async def get(self, id: Any) -> T: ...

    @abstractmethod
    async def all(self) -> list[T]: ...

    @abstractmethod
    async def delete(self, id: Any) -> bool: ...

    @abstractmethod
    async def update(self, id: str, data: dict) -> dict: ...

    @abstractmethod
    async def count(self) -> int: ...

    @abstractmethod
    async def exists(self, id: str) -> bool: ...


class SQLModelRepository(GenericRepository):
    """Base repository class for SQLModel entities"""

    model: Type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: T) -> T:
        obj = self.model(**data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        # self.session.expunge(obj)
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

    async def update(self, id: Any, data: T) -> T | None:
        obj = await self.session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**data.model_dump())
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
