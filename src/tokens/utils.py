from datetime import datetime, timedelta, timezone

import jwt

from tokens.config import JWT_SETTINGS


def encode_jwt(
    payload: dict,
    key: str = JWT_SETTINGS.private_key_path.read_text(),
    algorithm: str = JWT_SETTINGS.algorithm,
    expires_in: int = JWT_SETTINGS.access_token_expires_in_seconds,
) -> str:
    """Encode JWT token using private key and algorithm"""
    to_encode = payload.copy()

    utc_now = datetime.now(timezone.utc)
    expires_at = utc_now + timedelta(seconds=expires_in)
    to_encode.update(exp=expires_at, iat=utc_now)

    return jwt.encode(to_encode, key, algorithm=algorithm)


def decode_jwt(
    token: str | bytes,
    key: str = JWT_SETTINGS.public_key_path.read_text(),
    algorithm: str = JWT_SETTINGS.algorithm,
) -> dict:
    """Decode JWT token using public key and algorithm"""
    if not algorithm or algorithm.lower() == "none":
        raise ValueError("Secure algorithm is required")

    if isinstance(algorithm, list):
        raise ValueError("Algorithm must be a string, not a list")

    return jwt.decode(
        token,
        key,
        algorithms=[algorithm],
        options={
            "verify_signature": True,
            "verify_exp": True,
            "verify_iat": True,
            "verify_sub": True,
            "require": ["exp", "iat", "sub"],
        },
    )


test_payload = {
    "sub": "1234567890",
    "email": "test@test.com",
}


if __name__ == "__main__":
    test_token = encode_jwt(test_payload)
    print(test_token)

    test_decoded = decode_jwt(test_token)
    print(test_decoded)
