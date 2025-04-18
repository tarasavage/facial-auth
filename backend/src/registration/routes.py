from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

import tokens as token_utils
from cognito.user_dependency import CurrentUserDependency
from core.tags import Tags
from registration.decorators import protected_route
from registration.dependencies import (
    PERSON_IDENTITY_COOKIE_NAME,
    UserFromCookieDependency,
)
from registration.exceptions import ServiceError
from registration.schemas import (
    UserConfirmSignupCredentials,
    UserSignInCredentials,
)
from registration.service import (
    EmailConfirmationCommandDependency,
    GetUserProfileCommandDependency,
    RegisterUserCommandDependency,
    RegisterUserFaceCommandDependency,
    SigninViaFaceCommandDependency,
    SigninViaPasswordCommandDependency,
)
from users.schemas import CreateUser

router = APIRouter(tags=[Tags.REGISTRATION])


@router.post("/signup", status_code=status.HTTP_201_CREATED, tags=[Tags.DIRECT_AUTH])
@protected_route
async def register_user(user: CreateUser, command: RegisterUserCommandDependency) -> JSONResponse:
    try:
        await command.execute(user.model_dump())
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "User registered successfully"},
    )


@router.post("/confirm_signup", status_code=status.HTTP_200_OK, tags=[Tags.DIRECT_AUTH])
@protected_route
async def confirm_signup(
    confirm_signup_data: UserConfirmSignupCredentials,
    confirm_signup_command: EmailConfirmationCommandDependency,
) -> JSONResponse:
    """Confirm user registration with verification code."""
    try:
        await confirm_signup_command.execute(confirm_signup_data.email, confirm_signup_data.code)
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "User confirmed successfully"},
    )


@router.post("/signin", status_code=status.HTTP_200_OK, tags=[Tags.DIRECT_AUTH])
@protected_route
async def signin(
    signin_data: UserSignInCredentials,
    password_signin: SigninViaPasswordCommandDependency,
    face_signin: SigninViaFaceCommandDependency,
) -> JSONResponse:
    cookie = None
    if await face_signin.is_enabled(signin_data.email):
        cookie = token_utils.generate_access_token(payload=dict(email=signin_data.email))

    try:
        credentials = await password_signin.execute(signin_data.email, signin_data.password)
    except ServiceError as e:
        raise HTTPException(status_code=401, detail="Invalid credentials") from e

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Login successful",
            "access_token": credentials["AuthenticationResult"]["AccessToken"],
            "refresh_token": credentials["AuthenticationResult"]["RefreshToken"],
            "expires_in": credentials["AuthenticationResult"]["ExpiresIn"],
            "token_type": credentials["AuthenticationResult"]["TokenType"],
        },
    )

    if cookie is not None:
        response.set_cookie(
            key=PERSON_IDENTITY_COOKIE_NAME,
            value=f"Bearer {cookie.token}",
            httponly=True,
            secure=True,
            expires=cookie.expires_in,
        )

    return response


@router.post("/register_user_face", status_code=status.HTTP_201_CREATED, tags=[Tags.DIRECT_AUTH])
@protected_route
async def register_user_face(
    register_face_command: RegisterUserFaceCommandDependency,
    current_user: CurrentUserDependency,
    image: UploadFile = File(...),
) -> JSONResponse:
    image_bytes = await image.read()
    await register_face_command.execute(current_user.email, image_bytes)

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Face registered successfully for user"},
    )

    cookie = token_utils.generate_access_token(payload=dict(email=current_user.email))
    response.set_cookie(
        key=PERSON_IDENTITY_COOKIE_NAME,
        value=f"Bearer {cookie.token}",
        httponly=True,
        secure=True,
        expires=cookie.expires_in,
    )

    return response


@router.post("/signin_via_face", status_code=status.HTTP_200_OK, tags=[Tags.DIRECT_AUTH])
@protected_route
async def signin_via_face(
    signin_via_face_command: SigninViaFaceCommandDependency,
    user: UserFromCookieDependency,
    image: UploadFile = File(...),
) -> JSONResponse:
    image_bytes = await image.read()
    credentials = await signin_via_face_command.execute(user.email, image_bytes)

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Login successful",
            "access_token": credentials["AuthenticationResult"]["AccessToken"],
            "refresh_token": credentials["AuthenticationResult"]["RefreshToken"],
            "expires_in": credentials["AuthenticationResult"]["ExpiresIn"],
            "token_type": credentials["AuthenticationResult"]["TokenType"],
        },
    )

    cookie = token_utils.generate_access_token(payload=dict(email=user.email))
    response.set_cookie(
        key=PERSON_IDENTITY_COOKIE_NAME,
        value=f"Bearer {cookie.token}",
        httponly=True,
        secure=True,
        expires=cookie.expires_in,
    )

    return response


@router.get("/me", status_code=status.HTTP_200_OK, tags=[Tags.DIRECT_AUTH])
@protected_route
async def get_user_profile(
    get_user_profile_command: GetUserProfileCommandDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        user_profile = await get_user_profile_command.execute(current_user.email)
    except ServiceError as e:
        raise HTTPException(status_code=404, detail="User profile not found") from e

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "email": user_profile["email"],
            "email_verified": user_profile["email_verified"],
            "username": user_profile["username"],
            "face_image_key": user_profile["face_image_key"],
            "is_direct": user_profile["is_direct"],
        },
    )


@router.post("/check_face_auth", status_code=status.HTTP_200_OK, tags=[Tags.DIRECT_AUTH])
async def is_face_auth_enabled(
    user_from_cookie: UserFromCookieDependency,
    signin_via_face_command: SigninViaFaceCommandDependency,
) -> JSONResponse:
    """Check if user has a valid identity cookie for face authentication."""
    has_face_registered = await signin_via_face_command.is_enabled(user_from_cookie.email)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "can_use_face_auth": has_face_registered,
            "email": user_from_cookie.email,
        },
    )
