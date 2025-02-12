from typing import Annotated

import jwt
from pydantic import EmailStr
import requests
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.service import CognitoTokenServiceDependency
from core.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])

security = HTTPBearer()


def fetch_jwks(url: str) -> dict:
    keys = requests.get(url).json()["keys"]
    return {key["kid"]: key for key in keys}


JWKS = fetch_jwks(get_settings().AWS_COGNITO_JWKS_URL)


def verify_token(token: str, jwks: dict, audience: str) -> dict:
    header = jwt.get_unverified_header(token)
    if header["kid"] not in jwks:
        raise HTTPException(status_code=401, detail="Invalid token")

    jwk = jwks[header["kid"]]
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],

        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.MissingRequiredClaimError:
        raise HTTPException(status_code=401, detail="Missing required claims")
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

    return payload


def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    return verify_token(
        token=token.credentials,
        jwks=JWKS,
        audience=get_settings().AWS_COGNITO_CLIENT_ID,
    )


CurrentUserDependency = Annotated[dict, Depends(get_current_user)]


@router.post("/signin")
async def signin(user: EmailStr, pwd: str, cognito: CognitoTokenServiceDependency):
    return cognito.signin(user, pwd)


@router.post("/signup")
async def signup(user: EmailStr, pwd: str, cognito: CognitoTokenServiceDependency):
    return cognito.signup(user, pwd)


@router.post("/confirm_signup")
async def confirm_signup(user: EmailStr, code: str, cognito: CognitoTokenServiceDependency):
    return cognito.confirm_signup(user, code)


@router.post("/logout")
async def logout(
    cognito: CognitoTokenServiceDependency,
    token: HTTPAuthorizationCredentials = Depends(security),
):
    return cognito.logout(token.credentials)


@router.get("/me")
async def me(current_user: CurrentUserDependency):
    return current_user
