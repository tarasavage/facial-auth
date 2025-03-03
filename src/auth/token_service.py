from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.exceptions import NotAuthorizedError
from auth.schemas import Profile
from auth.service import CognitoTokenServiceDependency

BearerTokenDependency = Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())]


def validate_jwt_token(
    token: str,
    cognito: CognitoTokenServiceDependency,
) -> dict:
    """Validate JWT token using Cognito service."""
    try:
        return cognito.get_user_profile(token)
    except NotAuthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))


def get_current_user(
    cognito: CognitoTokenServiceDependency,
    token: BearerTokenDependency,
) -> Profile:
    """Get current user from JWT token."""
    user_data = validate_jwt_token(token=token.credentials, cognito=cognito)
    return Profile(
        username=user_data["username"],
        sub=user_data["attributes"]["sub"],
        email=user_data["attributes"]["email"],
        email_verified=user_data["attributes"]["email_verified"].lower() == "true",
    )


CurrentUserDependency = Annotated[Profile, Depends(get_current_user)]
