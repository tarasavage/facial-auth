from functools import lru_cache

from fastapi import Depends
from pydantic_settings import BaseSettings
from sqlalchemy import URL
from typing_extensions import Annotated


class Settings(BaseSettings):
    APP_NAME: str = "FaceLink"
    APP_SECRET_KEY: str

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_ENGINE: str = "postgresql+asyncpg"

    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY: str
    AWS_SECRET_ACCESS_KEY: str

    AWS_COGNITO_CLIENT_ID: str
    AWS_COGNITO_CLIENT_SECRET: str
    AWS_COGNITO_USER_POOL_ID: str

    @property
    def DATABASE_URI(self) -> str:
        return URL.create(
            drivername=self.DB_ENGINE,
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        ).render_as_string(hide_password=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDependency = Annotated[Settings, Depends(get_settings)]
