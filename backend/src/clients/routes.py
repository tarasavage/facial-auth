from fastapi import APIRouter, HTTPException, status

from clients.exceptions import ClientServiceError
from clients.schemas import ClientResponse, CreateClient
from clients.service import ClientServiceDependency
from cognito.user_dependency import CurrentUserDependency
from core.tags import Tags

router = APIRouter(tags=[Tags.CLIENTS])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": ClientResponse,
            "description": "Client created successfully",
        },
        status.HTTP_400_BAD_REQUEST: {"description": "Failed to create client"},
    },
)
async def create_client(
    client_service: ClientServiceDependency,
    user: CurrentUserDependency,
    client: CreateClient,
) -> ClientResponse:
    creation_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Failed to create client for user: {user.email}",
    )

    try:
        created_client = await client_service.create_client(client, user.email)
        client_data = created_client.model_dump()
    except ClientServiceError as e:
        raise creation_exception from e

    return ClientResponse(**client_data)
