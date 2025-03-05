import logging
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from core.db import get_session
from core.exceptions import UnitOfWorkError

logger = logging.getLogger(__name__)


class UnitOfWork:
    def __init__(self, session: Session) -> None:
        self.session = session

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            await self.rollback()
            logger.error("Transaction failed", exc_info=(exc_type, exc_value, traceback))
            raise UnitOfWorkError(
                f"Rolling back transaction due to exception: {exc_type.__name__} {exc_value}"
            ) from exc_value
        else:
            await self.commit()

        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


def get_unit_of_work(
    session: Annotated[Session, Depends(get_session)],
) -> UnitOfWork:
    return UnitOfWork(session)


UnitOfWorkDependency = Annotated[UnitOfWork, Depends(get_unit_of_work)]
