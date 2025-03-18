from pathlib import Path

from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent


class TokenConfig(BaseModel):
    PRIVATE_KEY_PATH: Path = BASE_DIR / "certs" / "private_key.pem"
    PUBLIC_KEY_PATH: Path = BASE_DIR / "certs" / "public_key.pem"
    ALGORITHM: str = "RS256"

    ACCESS_TOKEN_EXPIRES_IN_SECONDS: int = 604800  # 1 week
    REFRESH_TOKEN_EXPIRES_IN_SECONDS: int = 604800  # 1 week


JWT = TokenConfig()
