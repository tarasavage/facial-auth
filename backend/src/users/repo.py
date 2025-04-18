from typing import Annotated, Dict, Any

import sqlalchemy
from fastapi import Depends
from sqlmodel import Session

from core.db import get_session
from users.exceptions import (
    UserAlreadyExistsError,
    UserNotDeletedError,
    UserNotFoundError,
    UserNotUpdatedError,
)
from core.repository import SQLModelRepository
from users.models import User


class UsersUnitOfWork:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.user_repo = UserRepository(self.session)

    async def __aenter__(self) -> "UsersUnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()


class UserRepository(SQLModelRepository):
    model = User

    async def create(self, data: Dict[str, Any]) -> User:
        try:
            return await super().create(data)
        except sqlalchemy.exc.IntegrityError as e:
            raise UserAlreadyExistsError(e)

    async def get(self, id: int) -> User:
        user = await super().get(id)
        if user is None:
            raise UserNotFoundError("User with id {id} is not found")
        return user

    async def update(self, id: int, data: Dict[str, Any]) -> User:
        try:
            user = await super().update(id, data)
            if user is None:
                raise UserNotFoundError("User with id {id} is not found")
            return user
        except sqlalchemy.exc.ProgrammingError as e:
            raise UserNotUpdatedError("User with id {id} is not updated") from e

    async def delete(self, id: int) -> bool:
        try:
            user = await super().delete(id)
            if not user:
                raise UserNotFoundError("User with id {id} is not found")
            return user
        except sqlalchemy.exc.ProgrammingError as e:
            raise UserNotDeletedError("User with id {id} is not deleted") from e

    async def get_by_email(self, email: str) -> User:
        user = await super().filter(email=email)
        if not user:
            raise UserNotFoundError("User with email {email} is not found")
        return user[0]


def get_users_repository(
    session: Annotated[Session, Depends(get_session)],
) -> UserRepository:
    return UserRepository(session)


UserRepositoryDependency = Annotated[UserRepository, Depends(get_users_repository)]


def get_user_unit_of_work(
    session: Annotated[Session, Depends(get_session)],
) -> UsersUnitOfWork:
    return UsersUnitOfWork(session)


UserUnitOfWorkDependency = Annotated[UsersUnitOfWork, Depends(get_user_unit_of_work)]
