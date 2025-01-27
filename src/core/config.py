from functools import lru_cache

from pydantic_settings import BaseSettings
from sqlalchemy import URL


class Settings(BaseSettings):
    APP_NAME: str = "FaceLink"
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_ENGINE: str = "postgresql"

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
