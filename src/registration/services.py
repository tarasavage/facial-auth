from typing import Annotated

from botocore.exceptions import ClientError
from fastapi import Depends

from auth.exceptions import SignUpError
from auth.repository import CognitoRepo, CognitoRepoDependency
from core.db import SessionDependency
from core.exceptions import UnitOfWorkError
from core.unit_of_work import IUnitOfWork, UnitOfWork
from registration.exceptions import (
    FaceVerificationNotEnabledError,
    ServiceError,
)
from rekognition.exceptions import (
    FaceOccludedError,
    InvalidFaceCountError,
    SunglassesError,
)
from rekognition.repository import (
    RekognitionRepository,
    RekognitionRepositoryDependency,
)
from s3.exceptions import ImageTooLargeError
from s3.service import S3Service, S3ServiceDependency
from users.repo import UsersRepository
from users.schemas import CreateUser, UpdateUser

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB


class RegistrationService:
    def __init__(
        self,
        uow: IUnitOfWork,
        cognito_repo: CognitoRepo,
        users_repo: UsersRepository,
        rekognition_repo: RekognitionRepository,
        s3_repo: S3Service,
    ):
        self._uow = uow
        self._cognito = cognito_repo
        self._users = users_repo
        self._rekognition = rekognition_repo
        self._s3 = s3_repo

    async def register_user(self, user_data: CreateUser):
        try:
            async with self._uow:
                user = await self._users.create(user_data)

                try:
                    self._cognito.signup(user_data.email, user_data.password)
                except SignUpError as e:
                    raise ServiceError(f"Cognito signup failed: {e}") from e

                return user
        except UnitOfWorkError as e:
            raise ServiceError(f"Failed to register user: {e}") from e

    def confirm_signup(self, email: str, code: str):
        try:
            self._cognito.confirm_signup(email, code)
        except ClientError as e:
            raise ServiceError(f"Failed to confirm signup: {e}") from e

    async def signin(self, email: str, password: str) -> dict:
        try:
            async with self._uow:
                await self._users.get_by_email(email)
                tokens = self._cognito.signin(email, password)
                return tokens
        except UnitOfWorkError as e:
            raise ServiceError(f"Failed to signin: {e}") from e

    async def register_user_face(self, email: str, image: bytes):
        if len(image) > MAX_IMAGE_SIZE:
            raise ImageTooLargeError("Image is too large")

        try:
            async with self._uow:
                user = await self._users.get_by_email(email)

                face_details = self._rekognition.detect_face_details(image)
                self._validate_detected_face(face_details)

                user_data = UpdateUser(face_image_key=user.s3_face_image_key)
                await self._users.update(user.id, user_data)
                self._s3.upload_object(key=user.s3_face_image_key, file=image)

                return {
                    "status": "success",
                    "message": "User face registered successfully",
                }

        except UnitOfWorkError as e:
            raise ServiceError(f"Failed to register user face: {e}") from e

    def _validate_detected_face(self, face_details: dict):
        faces = face_details.get("FaceDetails", [])

        if number_of_faces := len(faces) != 1:
            raise InvalidFaceCountError(
                f"Image must contain exactly one face. Detected {number_of_faces} faces."
            )

        face = faces[0]
        if face.get("Sunglasses", {}).get("Value"):
            raise SunglassesError("Face image cannot contain sunglasses.")

        if face.get("FaceOccluded", {}).get("Value"):
            raise FaceOccludedError("Face image cannot be occluded.")

    async def verify_face(self, email: str, image: bytes):
        try:
            async with self._uow:
                user = await self._users.get_by_email(email)
                if not user.face_image_key:
                    raise FaceVerificationNotEnabledError(
                        "Face verification is not enabled for this user"
                    )

                self._rekognition.compare_faces(user.s3_face_image_key, image)
        except UnitOfWorkError as e:
            raise ServiceError(f"Failed to verify face: {e}") from e


def get_registration_service(
    session: SessionDependency,
    cognito_repo: CognitoRepoDependency,
    rekognition_repo: RekognitionRepositoryDependency,
    s3_repo: S3ServiceDependency,
) -> RegistrationService:
    return RegistrationService(
        uow=UnitOfWork(session),
        cognito_repo=cognito_repo,
        users_repo=UsersRepository(session),
        rekognition_repo=rekognition_repo,
        s3_repo=s3_repo,
    )


RegistrationServiceDependency = Annotated[
    RegistrationService, Depends(get_registration_service)
]


def get_registration_service_2(
    session: SessionDependency,
    cognito_repo: CognitoRepoDependency,
    rekognition_repo: RekognitionRepositoryDependency,
    s3_repo: S3ServiceDependency,
) -> RegistrationService:
    return RegistrationService(
        uow=UnitOfWork(session),
        cognito_repo=cognito_repo,
        users_repo=UsersRepository(session),
        rekognition_repo=rekognition_repo,
        s3_repo=s3_repo,
    )
