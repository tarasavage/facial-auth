from typing import Annotated
from boto3 import client
from botocore.exceptions import ClientError
from fastapi import Depends

from rekognition.config import RekognitionSettingsDependency
from rekognition.exceptions import RekognitionClientError


class RekognitionClient:
    def __init__(
        self, aws_access_key_id: str, aws_secret_access_key: str, region_name: str
    ):
        try:
            self.client = client(
                "rekognition",
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )
        except ClientError as e:
            raise RekognitionClientError(
                "Failed to initialize Rekognition client"
            ) from e

    @classmethod
    def from_settings(cls, settings) -> "RekognitionClient":
        """Factory method to create client from settings"""
        return cls(
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )


def get_rekognition_client(
    settings: RekognitionSettingsDependency,
) -> RekognitionClient:
    return RekognitionClient.from_settings(settings).client


RekognitionClientDependency = Annotated[
    RekognitionClient, Depends(get_rekognition_client)
]
