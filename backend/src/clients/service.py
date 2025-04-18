import uuid
from typing import Annotated

from fastapi import Depends

from clients.exceptions import ClientAlreadyExistsError, ClientNotFoundError, ClientServiceError
from clients.repository import ClientRepository, ClientRepositoryDependency
from clients.schemas import CreateClient
from users.repo import UserRepository, UserRepositoryDependency
from users.exceptions import UserNotFoundError


class ClientService:
    def __init__(self, repo: ClientRepository, user_repo: UserRepository):
        self.client_repo = repo
        self.user_repo = user_repo

    async def create_client(self, client: CreateClient, owner_email: str):
        client_data = client.model_dump()
        client_data.update(client_id=str(uuid.uuid4()))

        try:
            owner = await self.user_repo.get_by_email(owner_email)
            client_data.update(owner_id=owner.id)
        except UserNotFoundError as e:
            raise ClientServiceError(f"User not found: {e}") from e

        try:
            return await self.client_repo.create(client_data)
        except ClientAlreadyExistsError as e:
            raise ClientServiceError(f"Client already exists: {e}") from e

    async def get_client(self, client_id: str):
        try:
            return await self.client_repo.get_by_client_id(client_id)
        except ClientNotFoundError as e:
            raise ClientServiceError(f"Client not found: {e}") from e

    async def add_user_to_client(self, client_id: str, user_id: int):
        if not await self.client_repo.does_client_exist(client_id):
            raise ClientNotFoundError(f"Client with id {client_id} not found")

        if not await self.user_repo.does_user_exist(user_id):
            raise UserNotFoundError(f"User with id {user_id} not found")

        try:
            return await self.client_repo.link_user_to_client(client_id, user_id)
        except ClientNotFoundError as e:
            raise ClientServiceError(f"Client not found: {e}") from e


def get_client_service(client_repo: ClientRepositoryDependency, user_repo: UserRepositoryDependency) -> ClientService:
    return ClientService(client_repo, user_repo)


ClientServiceDependency = Annotated[ClientService, Depends(get_client_service)]
