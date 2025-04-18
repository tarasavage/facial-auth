from typing import Annotated

from fastapi import Depends

from users.models import User
from users.repo import UserUnitOfWorkDependency


class UsersService:
    def __init__(self, uow: UserUnitOfWorkDependency):
        self.uow = uow

    async def get_user(self, id: str) -> User:
        async with self.uow as uow:
            return await uow.user_repo.get(id)

    async def create_user(self, user: User) -> User:
        async with self.uow as uow:
            user = await uow.user_repo.create(user)
            await uow.commit()
            return user

    async def get_all_users(self) -> list[User]:
        async with self.uow as uow:
            return await uow.user_repo.all()

    async def delete_user(self, id: int) -> None:
        async with self.uow as uow:
            await uow.user_repo.delete(id)
            await uow.commit()

    async def update_user(self, id: int, user: User) -> None:
        async with self.uow as uow:
            await uow.user_repo.update(id, user)
            await uow.commit()

    async def get_user_by_email(self, email: str) -> User:
        async with self.uow as uow:
            return await uow.user_repo.get_by_email(email)


def get_users_service(uow: UserUnitOfWorkDependency) -> UsersService:
    return UsersService(uow)


UsersServiceDependency = Annotated[UsersService, Depends(get_users_service)]
