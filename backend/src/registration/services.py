import logging
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
from registration.schemas import (
    FaceRegistrationResult,
    RegisterUserFaceResponse,
    SignInViaFaceResponse,
)
from rekognition.repository import (
    RekognitionRepository,
    RekognitionRepositoryDependency,
)
from s3.service import S3Service, S3ServiceDependency
from tokens.schemas import AccessToken
from users.exception import UserNotFoundError
from users.model import User
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
                user = await self._get_user_or_error(email)

                try:
                    tokens = self._cognito.signin(email, password)
                except cognito_exceptions.AuthError as e:
                    raise ServiceError(f"AWS Cognito signin failed for user ({user.email}): {e}") from e

                return tokens

        except UnitOfWorkError as e:
            raise ServiceError(f"Failed to signin: {e}") from e

    async def register_face_and_issue_token(self, email: str, image: bytes) -> RegisterUserFaceResponse:
        user = await self._get_user_or_error(email)
        access_token = self._generate_access_token_for_user(user)

        try:
            response = await self._register_user_face(user, image)
        except ServiceError as e:
            await self._unregister_user_face(user)
            raise e

        return RegisterUserFaceResponse(
            message=response.message, token=access_token.token, expires_in=access_token.expires_in
        )

    async def verify_face(self, email: str, image: bytes):
        user = await self._get_user_or_error(email)
        try:
            await self._authenticate_face_image(user, image)
        except ServiceError as e:
            raise ServiceError(f"Failed to verify face: {e}") from e

    async def signin_via_face(self, email: str, image: bytes) -> SignInViaFaceResponse:
        user = await self._get_user_or_error(email)
        access_token = self._generate_access_token_for_user(user)

        try:
            await self._authenticate_face_image(user, image)
        except ServiceError as e:
            raise ServiceError(f"Failed to signin via face: {e}") from e

        return SignInViaFaceResponse(
            message="Login successful", token=access_token.token, expires_in=access_token.expires_in
        )

    async def check_if_face_auth_is_enabled(self, email: str) -> bool:
        try:
            user = await self._get_user_or_error(email)
            return user.face_image_key is not None
        except ServiceError:
            return False

    async def _unregister_user_face(self, user: User):
        try:
            async with self._uow:
                await self._users.update(user.id, {"face_image_key": None})

                try:
                    self._s3.delete_object(key=user.s3_face_image_key)
                except s3_exceptions.S3ServiceError as e:
                    logging.info(f"Failed to delete user face image from S3, it probably doesn't exist: {e}")

        except UnitOfWorkError as e:
            raise ServiceError(f"Failed to unregister user face: {e}") from e

    async def _get_user_or_error(self, email: str) -> User:
        try:
            return await self._users.get_by_email(email)
        except UserNotFoundError as e:
            raise ServiceError(f"Requested user ({email}) not found") from e

    async def _register_user_face(self, user: User, image: bytes):
        if len(image) > MAX_IMAGE_SIZE:
            raise s3_exceptions.ImageTooLargeError("Image is too large")

        try:
            async with self._uow:
                try:
                    face_details = self._rekognition.detect_face_details(image)
                    self._validate_detected_face(face_details)
                except rekognition_exceptions.RekognitionClientError as e:
                    raise ServiceError(f"Failed to register user face: {e}") from e

                await self._users.update(user.id, {"face_image_key": user.s3_face_image_key})
                self._s3.upload_object(key=user.s3_face_image_key, file=image)

                return FaceRegistrationResult.success(
                    message="User face registered successfully",
                    data={
                        "sub": user.id,
                        "email": user.email,
                    },
                )

        except UnitOfWorkError as e:
            raise ServiceError(f"Failed to register user face: {e}") from e

    def _generate_access_token_for_user(self, user: User) -> AccessToken:
        payload = self._generate_payload_for_access_token(user)
        return self._generate_access_token(payload=payload)

    def _generate_access_token(self, payload: dict) -> AccessToken:
        payload = payload.copy()
        payload.update(token_type="access")

        expires_in = tokens.JWT.ACCESS_TOKEN_EXPIRES_IN_SECONDS
        token = tokens.encode_jwt(payload, expires_in=expires_in)

        return AccessToken(access_token=token, expires_in=expires_in)

    def _generate_payload_for_access_token(self, user: User) -> dict:
        return {"email": user.email, "sub": f"{user.id}"}

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

    async def _authenticate_face_image(self, user: User, image: bytes):
        try:
            async with self._uow:
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
