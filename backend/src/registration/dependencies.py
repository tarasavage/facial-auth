from typing import Optional

from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

from registration.schemas import CookieProfile
from tokens.utils import decode_jwt

from typing_extensions import Annotated, Doc


PERSON_IDENTITY_COOKIE_NAME = "__PersonIdentityToken"


class HttpBearerWithCookie(HTTPBearer):
    def __init__(
        self,
        *,
        bearerFormat: Annotated[Optional[str], Doc("Bearer token format.")] = None,
        scheme_name: Annotated[
            Optional[str],
            Doc(
                """
                Security scheme name.

                It will be included in the generated OpenAPI (e.g. visible at `/docs`).
                """
            ),
        ] = None,
        description: Annotated[
            Optional[str],
            Doc(
                """
                Security scheme description.

                It will be included in the generated OpenAPI (e.g. visible at `/docs`).
                """
            ),
        ] = None,
        auto_error: Annotated[
            bool,
            Doc(
                """
                By default, if the HTTP Bearer token is not provided (in an
                `Authorization` header), `HTTPBearer` will automatically cancel the
                request and send the client an error.

                If `auto_error` is set to `False`, when the HTTP Bearer token
                is not available, instead of erroring out, the dependency result will
                be `None`.

                This is useful when you want to have optional authentication.

                It is also useful when you want to have authentication that can be
                provided in one of multiple optional ways (for example, in an HTTP
                Bearer token or in a cookie).
                """
            ),
        ] = True,
        auth_cookie_name: Annotated[
            str,
            Doc("The name of the cookie that contains the authentication token."),
        ],
    ):
        super().__init__(
            bearerFormat=bearerFormat,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )
        self.auth_cookie_name = auth_cookie_name

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        authorization = request.cookies.get(self.auth_cookie_name)
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")
            else:
                return None

        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Invalid authentication credentials",
                )
            else:
                return None

        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


CookieBearerTokenDependency = Annotated[
    HTTPAuthorizationCredentials, Depends(HttpBearerWithCookie(auth_cookie_name=PERSON_IDENTITY_COOKIE_NAME))
]


def get_user_from_cookie(token: CookieBearerTokenDependency) -> CookieProfile:
    try:
        encrypted_token = decode_jwt(token.credentials)
        return CookieProfile(
            email=encrypted_token["email"],
            sub=encrypted_token["sub"],
        )
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e)) from e


UserFromCookieDependency = Annotated[CookieProfile, Depends(get_user_from_cookie)]
