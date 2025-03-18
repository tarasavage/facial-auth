from pydantic import BaseModel, Field


class TokenData(BaseModel):
    """Base model for token data"""

    token: str
    expires_in: int


class AccessToken(TokenData):
    """Access token response model"""

    token: str = Field(..., alias="access_token")
    token_type: str = "bearer"


class RefreshToken(TokenData):
    """Refresh token response model"""

    token: str = Field(..., alias="refresh_token")
    token_type: str = "bearer"


class TokenPair(BaseModel):
    """Token pair with access and refresh tokens"""

    access_token: AccessToken
    refresh_token: RefreshToken
