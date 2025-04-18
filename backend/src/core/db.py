from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from core.config import get_settings
from typing import Annotated, AsyncGenerator, TypeAlias


engine = create_async_engine(get_settings().DATABASE_URI)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session


SessionDependency: TypeAlias = Annotated[AsyncSession, Depends(get_session)]
