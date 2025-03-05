from typing import Annotated
from boto3 import client
from botocore.exceptions import ClientError
from fastapi import Depends

from s3.config import S3SettingsDependency
from s3.exceptions import S3ClientError


class S3Client:
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, region_name: str):
        try:
            self.client = client(
                "s3",
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )
        except ClientError as e:
            raise S3ClientError("Failed to initialize S3 client") from e

    @classmethod
    def from_settings(cls, settings) -> "S3Client":
        """Factory method to create client from settings"""
        return cls(
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )


def get_s3_client(settings: S3SettingsDependency) -> S3Client:
    return S3Client.from_settings(settings).client


S3ClientDependency = Annotated[S3Client, Depends(get_s3_client)]
