from typing import Annotated

from fastapi import Depends

import cognito.exceptions as cognito_exceptions
import rekognition.exceptions as rekognition_exceptions
import s3.exceptions as s3_exceptions
import tokens
from cognito.service import CognitoTokenServiceDependency
from core.db import SessionDependency
from core.exceptions import UnitOfWorkError
from core.unit_of_work import UnitOfWork
from registration.exceptions import (
    FaceVerificationNotEnabledError,
    ServiceError,
)
from rekognition.repository import (
    RekognitionRepository,
    RekognitionRepositoryDependency,
)
from s3.service import S3Service, S3ServiceDependency
from users.exception import UserNotFoundError
from users.repo import UsersRepository
from users.schemas import CreateUser

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB


class RegistrationService:
    def __init__(
        self,
        uow: UnitOfWork,
        cognito_service: CognitoTokenServiceDependency,
        users_repo: UsersRepository,
        rekognition_repo: RekognitionRepository,
        s3_repo: S3Service,
    ):
        self._uow = uow
        self._cognito = cognito_service
        self._users = users_repo
        self._rekognition = rekognition_repo
        self._s3 = s3_repo

    async def get_user_profile(self, email: str) -> dict:
        try:
            async with self._uow:
                try:
                    user = await self._users.get_by_email(email)
                except UserNotFoundError as e:
                    raise ServiceError("Requested user not found") from e

                return user.model_dump()

        except UnitOfWorkError as e:
            raise ServiceError(f"Failed to get user profile: {e}") from e

    async def register_user(self, user_data: CreateUser):
        try:
            async with self._uow:
                user = await self._users.create(user_data.model_dump())

                try:
                    self._cognito.signup(user_data.email, user_data.password)
                except cognito_exceptions.SignUpError as e:
                    raise ServiceError(f"Cognito signup failed: {e}") from e

                return user
        except UnitOfWorkError as e:
            raise ServiceError(f"Failed to register user: {e}") from e

    async def confirm_signup(self, email: str, code: str) -> None:
        try:
            async with self._uow:
                user = await self._users.get_by_email(email)
                if user.email_verified:
                    raise ServiceError("User has already been confirmed")

                await self._users.update(user.id, {"email_verified": True})

                try:
                    self._cognito.confirm_signup(email, code)
                except cognito_exceptions.AuthError as e:
                    raise ServiceError(f"AWS Cognito confirmation failed: {e}") from e

        except UnitOfWorkError as e:
            raise ServiceError(f"Database error during signup confirmation: {e}") from e

    async def signin(self, email: str, password: str) -> dict:
        try:
            async with self._uow:
                try:
                    await self._users.get_by_email(email)
                except UserNotFoundError as e:
                    raise ServiceError(f"User ({email}) not found") from e

                try:
                    tokens = self._cognito.signin(email, password)
                except cognito_exceptions.AuthError as e:
                    raise ServiceError(f"AWS Cognito signin failed: {e}") from e

                return tokens

        except UnitOfWorkError as e:
            raise ServiceError(f"Failed to signin: {e}") from e

    async def register_user_face(self, email: str, image: bytes):
        if len(image) > MAX_IMAGE_SIZE:
            raise s3_exceptions.ImageTooLargeError("Image is too large")

        try:
            async with self._uow:
                try:
                    user = await self._users.get_by_email(email)
                except UserNotFoundError as e:
                    raise ServiceError("Requested user not found") from e

                face_details = self._rekognition.detect_face_details(image)
                self._validate_detected_face(face_details)

                await self._users.update(user.id, {"face_image_key": user.s3_face_image_key})
                self._s3.upload_object(key=user.s3_face_image_key, file=image)

                tokens = self.generate_jwt_tokens(
                    payload={
                        "sub": user.id,
                        "email": user.email,
                        "email_verified": user.email_verified,
                        "face_image_key": user.s3_face_image_key,
                    }
                )

                return {
                    "status": "success",
                    "message": "User face registered successfully",
                    **tokens,
                }

        except UnitOfWorkError as e:
            raise ServiceError(f"Failed to register user face: {e}") from e

    def generate_jwt_tokens(self, payload: dict) -> dict:
        return {
            "access_token": tokens.create_access_token(payload),
            "refresh_token": tokens.create_refresh_token(payload),
            "expires_in": tokens.JWT.ACCESS_TOKEN_EXPIRES_IN_SECONDS,
        }

    def _validate_detected_face(self, face_details: dict):
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

    async def verify_face(self, email: str, image: bytes):
        try:
            async with self._uow:
                user = await self._users.get_by_email(email)
                if not user.face_image_key:
                    raise FaceVerificationNotEnabledError("Face verification is not enabled for this user")

                try:
                    self._rekognition.compare_faces(user.s3_face_image_key, image)
                except rekognition_exceptions.RekognitionError as e:
                    raise ServiceError(f"Failed to verify face: {e}") from e

        except UnitOfWorkError as e:
            raise ServiceError(f"Failed to verify face: {e}") from e


def get_registration_service(
    session: SessionDependency,
    cognito_service: CognitoTokenServiceDependency,
    rekognition_repo: RekognitionRepositoryDependency,
    s3_repo: S3ServiceDependency,
) -> RegistrationService:
    return RegistrationService(
        uow=UnitOfWork(session),
        cognito_service=cognito_service,
        users_repo=UsersRepository(session),
        rekognition_repo=rekognition_repo,
        s3_repo=s3_repo,
    )


RegistrationServiceDependency = Annotated[RegistrationService, Depends(get_registration_service)]
