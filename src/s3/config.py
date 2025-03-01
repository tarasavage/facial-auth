from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings


class S3Config(BaseSettings):
    AWS_ACCESS_KEY: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str

    AWS_S3_BUCKET_NAME: str


@lru_cache
def get_s3_config() -> S3Config:
    return S3Config()


S3SettingsDependency = Annotated[S3Config, Depends(get_s3_config)]
