from datetime import datetime, timedelta, timezone

import jwt

from tokens.config import JWT
from tokens.schemas import AccessToken


def encode_jwt(
    payload: dict,
    key: str = JWT.PRIVATE_KEY_PATH.read_text(),
    algorithm: str = JWT.ALGORITHM,
    expires_in: int = JWT.ACCESS_TOKEN_EXPIRES_IN_SECONDS,
) -> str:
    """Encode JWT token using private key and algorithm"""
    to_encode = payload.copy()

    utc_now = datetime.now(timezone.utc)
    expires_at = utc_now + timedelta(seconds=expires_in)
    to_encode.update(exp=expires_at, iat=utc_now)

    return jwt.encode(to_encode, key, algorithm=algorithm)


def decode_jwt(
    token: str | bytes,
    key: str = JWT.PUBLIC_KEY_PATH.read_text(),
    algorithm: str = JWT.ALGORITHM,
) -> dict:
    """Decode JWT token using public key and algorithm"""
    if algorithm.lower() == "none":
        raise ValueError("Secure algorithm is required")

    return jwt.decode(
        token,
        key,
        algorithms=[algorithm],
        options={
            "verify_signature": True,
            "verify_exp": True,
            "verify_iat": True,
            "require": ["exp", "iat"],
        },
    )


def generate_access_token(payload: dict) -> AccessToken:
    payload = payload.copy()
    payload.update(token_type="access")

    expires_in = JWT.ACCESS_TOKEN_EXPIRES_IN_SECONDS
    token = encode_jwt(payload, expires_in=expires_in)

    return AccessToken(access_token=token, expires_in=expires_in)
