from typing import List

from fastapi import APIRouter, HTTPException, status

from users.exception import UserAlreadyExistsError, UserNotFoundError
from core.schemas import MessageResponse
from users.schemas import CreateUser, UpdateUser, UserResponse
from users.service import UsersServiceDependency

router = APIRouter(prefix="", tags=["users"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
async def create_user(
    user: CreateUser, users_service: UsersServiceDependency
) -> UserResponse:
    try:
        user = await users_service.create_user(user)
        return user
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        ) from e


@router.get(
    "",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
)
async def list_users(users_service: UsersServiceDependency) -> List[UserResponse]:
    return await users_service.get_all_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    user_id: int, users_service: UsersServiceDependency
) -> UserResponse | None:
    try:
        return await users_service.get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        ) from e


@router.patch(
    "/{user_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: int, user: UpdateUser, users_service: UsersServiceDependency
) -> MessageResponse:
    try:
        await users_service.update_user(user_id, user)
        return MessageResponse(message="User updated successfully")
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        ) from e


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    user_id: int, users_service: UsersServiceDependency
) -> MessageResponse:
    try:
        await users_service.delete_user(user_id)
        return MessageResponse(message="User deleted successfully")
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        ) from e
