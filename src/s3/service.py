from io import BytesIO
from typing import Annotated

from fastapi import Depends
from s3.client import S3Client
from botocore.exceptions import ClientError

from s3.config import S3SettingsDependency
from s3.exceptions import S3ServiceError


class S3Service:
    def __init__(self, client: S3Client, bucket_name: str):
        self.client = client
        self.bucket_name = bucket_name

    def upload_object(self, key: str, file: bytes):
        """Upload an object to S3."""
        file_obj = BytesIO(file)

        try:
            self.client.upload_fileobj(file_obj, self.bucket_name, key)
        except ClientError as e:
            raise S3ServiceError("Failed to upload object to S3") from e


def get_s3_service(
    s3_config: S3SettingsDependency,
) -> S3Service:
    return S3Service(
        client=S3Client.from_settings(s3_config).client,
        bucket_name=s3_config.AWS_S3_BUCKET_NAME,
    )


S3ServiceDependency = Annotated[S3Service, Depends(get_s3_service)]
