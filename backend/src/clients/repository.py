from contextlib import asynccontextmanager
from typing import Annotated

import sqlalchemy
from fastapi import Depends

from clients.exceptions import ClientAlreadyExistsError, ClientNotFoundError
from clients.models import Client, ClientUserLink
from core.db import SessionDependency
from core.repository import SQLModelRepository


class ClientRepository(SQLModelRepository):
    model = Client

    @asynccontextmanager
    async def transaction(self):
        """Handle transaction boundaries"""
        try:
            yield
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def create(self, data: dict) -> Client:
        try:
            async with self.transaction():
                client = await super().create(data)

            await self.session.refresh(client)
            return client

        except sqlalchemy.exc.IntegrityError as e:
            raise ClientAlreadyExistsError(e) from e

    async def get_by_client_id(self, client_id: str) -> Client:
        client = await super().filter(client_id=client_id)
        if not client:
            raise ClientNotFoundError(f"Client with id {client_id} not found")
        return client[0]

    async def does_client_exist(self, client_id: str) -> bool:
        return await super().exists(id=client_id)

    async def link_user_to_client(self, client_id: str, user_id: int) -> ClientUserLink:
        link = ClientUserLink(client_id=client_id, user_id=user_id)
        self.session.add(link)
        await self.session.flush()
        return link


def get_client_repository(session: SessionDependency) -> ClientRepository:
    return ClientRepository(session)


ClientRepositoryDependency = Annotated[ClientRepository, Depends(get_client_repository)]
