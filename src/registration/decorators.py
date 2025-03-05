from functools import wraps

from fastapi import HTTPException, status

from registration.exceptions import ServiceError


def protected_route(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ServiceError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return wrapper
