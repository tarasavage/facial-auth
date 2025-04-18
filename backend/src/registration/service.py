import logging
from abc import ABC, abstractmethod
from typing import Annotated, Any

from fastapi import Depends

import cognito.exceptions as cognito_exceptions
import rekognition.exceptions as rekognition_exceptions
import s3.exceptions as s3_exceptions
from clients import exceptions as client_exceptions
from clients.service import ClientService, ClientServiceDependency
from cognito.service import CognitoTokenService, CognitoTokenServiceDependency
from core.exceptions import UnitOfWorkError
from core.unit_of_work import UnitOfWork, UnitOfWorkDependency
from registration.exceptions import ServiceError
from rekognition.service import RekognitionService, RekognitionServiceDependency
from s3.service import S3Service, S3ServiceDependency
from users.exceptions import UserNotFoundError
from users.models import User
from users.repo import UserRepository, UserRepositoryDependency


class RegisterCommand(ABC):
    @abstractmethod
    async def execute(self, user_data: dict) -> User:
        pass


class RegisterUserCommand(RegisterCommand):
    def __init__(self, uow: UnitOfWork, cognito: CognitoTokenService, users: UserRepository):
        self.uow = uow
        self.cognito = cognito
        self.users = users

    async def execute(self, user_data: dict) -> User:
        async with self.uow:
            user = await self.users.create(user_data)
            try:
                self.cognito.signup(user_data["email"], user_data["password"])
            except cognito_exceptions.SignUpError as e:
                raise ServiceError(f"Cognito signup failed: {e}") from e

            return user


def get_register_user_command(
    uow: UnitOfWorkDependency,
    cognito: CognitoTokenServiceDependency,
    users: UserRepositoryDependency,
) -> RegisterUserCommand:
    return RegisterUserCommand(uow, cognito, users)


RegisterUserCommandDependency = Annotated[RegisterUserCommand, Depends(get_register_user_command)]


class RegisterUserToClientCommand(RegisterCommand):
    def __init__(self, uow: UnitOfWork, cognito: CognitoTokenService, users: UserRepository, clients: ClientService):
        self.uow = uow
        self.cognito = cognito
        self.users = users
        self.clients = clients

    async def execute(self, user_data: dict) -> User:
        async with self.uow:
            user = await self.users.create(user_data)

            try:
                await self.clients.link_user_to_client(user_data["client_id"], user.id)
                self.cognito.signup(user_data["email"], user_data["password"])

            except client_exceptions.ClientNotFoundError as e:
                raise ServiceError(f"Client does not exist: {e}") from e

            except cognito_exceptions.SignUpError as e:
                raise ServiceError(f"Cognito signup failed: {e}") from e

            return user


def get_register_user_to_client_command(
    uow: UnitOfWorkDependency,
    cognito: CognitoTokenServiceDependency,
    users: UserRepositoryDependency,
    clients: ClientServiceDependency,
) -> RegisterUserToClientCommand:
    return RegisterUserToClientCommand(uow, cognito, users, clients)


RegisterUserToClientCommandDependency = Annotated[
    RegisterUserToClientCommand, Depends(get_register_user_to_client_command)
]


class RegisterUserFaceCommand(RegisterCommand):
    def __init__(
        self,
        uow: UnitOfWork,
        cognito: CognitoTokenService,
        users: UserRepository,
        rekognition: RekognitionService,
        s3: S3Service,
        max_image_size: int = 10 * 1024 * 1024,
    ):
        self.uow = uow
        self.cognito = cognito
        self.users = users
        self.rekognition = rekognition
        self.s3 = s3
        self.max_image_size = max_image_size

    async def execute(self, email: str, image: bytes) -> User:
        try:
            return await self.register_face(email, image)
        except UnitOfWorkError as e:
            await self.rollback(email)
            raise ServiceError(f"Failed to register user face: {e}") from e

    async def register_face(self, email: str, image: bytes) -> User:
        if len(image) > self.max_image_size:
            raise s3_exceptions.ImageTooLargeError("Image is too large")

        try:
            face_details = self.rekognition.detect_face_details(image)
            self.validate_face_on_registration(face_details)
        except rekognition_exceptions.RekognitionClientError as e:
            raise ServiceError(f"Failed to register user face: {e}") from e

        async with self.uow:
            user = await self.users.get_by_email(email)
            await self.users.update(user.id, {"face_image_key": user.s3_face_image_key})
            self.s3.upload_object(key=user.s3_face_image_key, file=image)

            return user

    async def rollback(self, email: str) -> None:
        with self.uow:
            user = await self.users.get_by_email(email)
            await self.users.update(user.id, {"face_image_key": None})

            try:
                self.s3.delete_object(key=user.s3_face_image_key)
            except s3_exceptions.S3ServiceError as e:
                logging.info(f"Failed to delete user face image from S3, it probably doesn't exist: {e}")

    def validate_face_on_registration(self, face_details: dict) -> None:
        faces = face_details.get("FaceDetails", [])

        if number_of_faces := len(faces) != 1:
            raise rekognition_exceptions.InvalidFaceCountError(
                f"Image must contain exactly one face. Detected {number_of_faces} faces."
            )

        face = faces[0]
        if face.get("Sunglasses", {}).get("Value"):
            raise rekognition_exceptions.SunglassesError("Face image cannot contain sunglasses.")

        if face.get("FaceOccluded", {}).get("Value"):
            raise rekognition_exceptions.FaceOccludedError("Face image cannot be occluded.")


def get_register_user_face_command(
    uow: UnitOfWorkDependency,
    cognito: CognitoTokenServiceDependency,
    users: UserRepositoryDependency,
    rekognition: RekognitionServiceDependency,
    s3: S3ServiceDependency,
) -> RegisterUserFaceCommand:
    return RegisterUserFaceCommand(uow, cognito, users, rekognition, s3)


RegisterUserFaceCommandDependency = Annotated[RegisterUserFaceCommand, Depends(get_register_user_face_command)]


class ConfirmSignupCommand(ABC):
    @abstractmethod
    async def execute(self, email: str, code: str) -> None:
        pass


class EmailConfirmationCommand(ConfirmSignupCommand):
    def __init__(self, uow: UnitOfWork, cognito: CognitoTokenService, users: UserRepository):
        self.uow = uow
        self.cognito = cognito
        self.users = users

    async def execute(self, email: str, code: str) -> None:
        async with self.uow:
            user = await self.users.get_by_email(email)
            if user.email_verified:
                raise ServiceError("User has already been confirmed")

            await self.users.update(user.id, {"email_verified": True})

        try:
            self.cognito.confirm_signup(email, code)
        except cognito_exceptions.AuthError as e:
            raise ServiceError(f"AWS Cognito confirmation failed: {e}") from e


def get_email_confirmation_command(
    uow: UnitOfWorkDependency,
    cognito: CognitoTokenServiceDependency,
    users: UserRepositoryDependency,
) -> EmailConfirmationCommand:
    return EmailConfirmationCommand(uow, cognito, users)


EmailConfirmationCommandDependency = Annotated[EmailConfirmationCommand, Depends(get_email_confirmation_command)]


class GetProfileCommand(ABC):
    @abstractmethod
    async def execute(self, email: str) -> dict:
        pass


class GetUserProfileCommand(GetProfileCommand):
    def __init__(self, users: UserRepository):
        self.users = users

    async def execute(self, email: str) -> dict:
        try:
            user = await self.users.get_by_email(email)
            return user.model_dump()
        except UserNotFoundError as e:
            raise ServiceError(f"Requested user ({email}) not found") from e


def get_get_user_profile_command(users: UserRepositoryDependency) -> GetUserProfileCommand:
    return GetUserProfileCommand(users)


GetUserProfileCommandDependency = Annotated[GetUserProfileCommand, Depends(get_get_user_profile_command)]


class SigninCommand(ABC):
    @abstractmethod
    async def execute(self, email: str, key: Any) -> dict:
        pass

    @abstractmethod
    async def is_enabled(self, email: str) -> bool:
        pass


class SigninViaPasswordCommand(SigninCommand):
    def __init__(self, cognito: CognitoTokenService, users: UserRepository):
        self.cognito = cognito
        self.users = users

    async def execute(self, email: str, key: str) -> dict:
        try:
            user = await self.users.get_by_email(email)
            return self.cognito.signin(email, key)
        except UserNotFoundError as e:
            raise ServiceError(f"Requested user ({email}) not found") from e

        except cognito_exceptions.AuthError as e:
            raise ServiceError(f"AWS Cognito signin failed for user ({user.email}): {e}") from e

    async def is_enabled(self, email: str) -> bool:
        return True


def get_signin_via_password_command(
    cognito: CognitoTokenServiceDependency,
    users: UserRepositoryDependency,
) -> SigninViaPasswordCommand:
    return SigninViaPasswordCommand(cognito, users)


SigninViaPasswordCommandDependency = Annotated[SigninViaPasswordCommand, Depends(get_signin_via_password_command)]


class SigninViaFaceCommand(SigninCommand):
    def __init__(self, cognito: CognitoTokenService, users: UserRepository, rekognition: RekognitionService):
        self.cognito = cognito
        self.users = users
        self.rekognition = rekognition

    async def execute(self, email: str, key: bytes) -> dict:
        if not await self.any_face_on_image_matches(email, key):
            raise ServiceError("Face authentication is not enabled for this user")

        return self.cognito.signin_via_face(email, key, "face_verified")

    async def any_face_on_image_matches(self, email: str, image: bytes) -> bool:
        try:
            user = await self.users.get_by_email(email)
            matches = self.rekognition.compare_faces(user.s3_face_image_key, image)
            return any(match["Matched"] for match in matches)
        except UserNotFoundError as e:
            raise ServiceError(f"Requested user ({email}) not found") from e

        except rekognition_exceptions.RekognitionError as e:
            raise ServiceError(f"Rekognition error: {e}") from e

    async def is_enabled(self, email: str) -> bool:
        try:
            user = await self.users.get_by_email(email)
            return bool(user.face_image_key)
        except UserNotFoundError:
            return False


def get_signin_via_face_command(
    cognito: CognitoTokenServiceDependency,
    users: UserRepositoryDependency,
    rekognition: RekognitionServiceDependency,
) -> SigninViaFaceCommand:
    return SigninViaFaceCommand(cognito, users, rekognition)


SigninViaFaceCommandDependency = Annotated[SigninViaFaceCommand, Depends(get_signin_via_face_command)]
