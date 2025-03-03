from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import EmailStr

from auth.service import CognitoTokenServiceDependency
from auth.token_service import BearerTokenDependency, CurrentUserDependency
from users.exception import UserAlreadyExistsError, UserNotFoundError
from users.schemas import CreateUser
from users.service import UsersServiceDependency

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
async def signup(
    user: CreateUser,
    cognito: CognitoTokenServiceDependency,
    users_service: UsersServiceDependency,
) -> JSONResponse:
    """Register a new user."""
    cognito.signup(user=user.email, pwd=user.password)

    try:
        user = await users_service.create_user(user)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=400, detail="User already exists")

    return JSONResponse(
        status_code=200,
        content={"message": "User signed up successfully"},
    )


@router.post("/confirm_signup")
async def confirm_signup(
    user: EmailStr,
    code: str,
    cognito: CognitoTokenServiceDependency,
) -> dict:
    """Confirm user registration with verification code."""
    return cognito.confirm_signup(user, code)


@router.post("/signin")
async def signin(
    user: EmailStr,
    password: str,
    cognito: CognitoTokenServiceDependency,
    users_service: UsersServiceDependency,
) -> JSONResponse:
    """Authenticate user and return access tokens."""
    tokens = cognito.signin(user, password)

    try:
        await users_service.get_user_by_email(user)
    except UserNotFoundError:
        raise HTTPException(status_code=401, detail="User has not been created yet")

    return JSONResponse(
        status_code=200,
        content={
            "message": "User signed in successfully",
            "access_token": tokens["AuthenticationResult"]["AccessToken"],
            "refresh_token": tokens["AuthenticationResult"]["RefreshToken"],
            "expires_in": tokens["AuthenticationResult"]["ExpiresIn"],
            "token_type": tokens["AuthenticationResult"]["TokenType"],
        },
    )


@router.post("/logout")
async def logout(
    cognito: CognitoTokenServiceDependency,
    token: BearerTokenDependency,
) -> dict:
    """Logout user and invalidate their token."""
    return cognito.logout(token.credentials)


@router.get("/me")
async def me(current_user: CurrentUserDependency) -> dict:
    """Get current user's profile."""
    return current_user
