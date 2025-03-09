from pathlib import Path

from pydantic import BaseModel


class TokenConfig(BaseModel):
    private_key_path: Path = Path("certs/private_key.pem")
    public_key_path: Path = Path("certs/public_key.pem")
    algorithm: str = "RS256"
    access_token_expires_in_seconds: int = 3600


JWT_SETTINGS = TokenConfig()
