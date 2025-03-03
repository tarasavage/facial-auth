from typing import Annotated

from fastapi import Depends

from rekognition.client import RekognitionClient, RekognitionClientDependency
from rekognition.exceptions import (
    FaceImageValidationError,
    RekognitionClientError,
    RekognitionLimitExceededError,
)


class RekognitionRepository:
    def __init__(self, rekognition_client: RekognitionClient):
        self.client = rekognition_client
        self.bucket_name = "facelinq"

    def compare_faces(
        self,
        source_image_key: str,
        target_image: bytes,
        similarity_threshold: float = 95.0,
    ) -> dict:
        try:
            return self.client.compare_faces(
                SourceImage={
                    "S3Object": {
                        "Bucket": self.bucket_name,
                        "Name": source_image_key,
                    }
                },
                TargetImage={"Bytes": target_image},
                SimilarityThreshold=similarity_threshold,
            )
        except (
            self.client.exceptions.InvalidImageFormatException,
            self.client.exceptions.InvalidParameterException,
            self.client.exceptions.InvalidS3ObjectException,
            self.client.exceptions.ImageTooLargeException,
        ) as e:
            raise FaceImageValidationError(
                "Invalid image parameters or format"
            ) from e
        except (
            self.client.exceptions.ProvisionedThroughputExceededException,
            self.client.exceptions.ThrottlingException,
            self.client.exceptions.InternalServerError,
        ) as e:
            raise RekognitionLimitExceededError(
                "Failed to send request to Rekognition"
            ) from e
        except self.client.exceptions.AccessDeniedException as e:
            raise RekognitionLimitExceededError(
                "Access denied to Rekognition service"
            ) from e

    def detect_face_details(self, image: bytes) -> dict:
        try:
            return self.client.detect_faces(
                Image={"Bytes": image},
                Attributes=["SUNGLASSES", "FACE_OCCLUDED"],
            )
        except self.client.exceptions.ClientError as e:
            raise RekognitionClientError("Failed to detect face details") from e


def get_rekognition_repository(
    client: RekognitionClientDependency,
) -> RekognitionRepository:
    return RekognitionRepository(client)


RekognitionRepositoryDependency = Annotated[
    RekognitionRepository, Depends(get_rekognition_repository)
]
