from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings


class RekognitionSettings(BaseSettings):
    AWS_ACCESS_KEY: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str

    AWS_REKOGNITION_SIMILARITY_THRESHOLD: float = 0.95
    AWS_REKOGNITION_COLLECTION_ID: str


@lru_cache
def get_rekognition_settings() -> RekognitionSettings:
    return RekognitionSettings()


RekognitionSettingsDependency = Annotated[RekognitionSettings, Depends(get_rekognition_settings)]
