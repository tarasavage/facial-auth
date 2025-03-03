from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from auth.token_service import CurrentUserDependency
from registration.decorators import protected_route
from registration.exceptions import ServiceError
from registration.schemas import (
    UserConfirmSignupCredentials,
    UserSignInCredentials,
)
from registration.services import RegistrationServiceDependency
from users.schemas import CreateUser

router = APIRouter(tags=["registration"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
@protected_route
async def register_user(
    user: CreateUser,
    registration_service: RegistrationServiceDependency,
) -> JSONResponse:
    """Register a new user."""
    try:
        await registration_service.register_user(user)
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "User registered successfully"},
    )


@router.post("/confirm_signup", status_code=status.HTTP_200_OK)
@protected_route
async def confirm_signup(
    confirm_signup_data: UserConfirmSignupCredentials,
    registration_service: RegistrationServiceDependency,
) -> JSONResponse:
    """Confirm user registration with verification code."""
    try:
        registration_service.confirm_signup(
            email=confirm_signup_data.email, code=confirm_signup_data.code
        )
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "User confirmed successfully"},
    )


@router.post("/signin", status_code=status.HTTP_200_OK)
@protected_route
async def signin(
    signin_data: UserSignInCredentials,
    registration_service: RegistrationServiceDependency,
) -> JSONResponse:
    """Authenticate user and return access tokens."""
    tokens = await registration_service.signin(signin_data.email, signin_data.password)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "User signed in successfully",
            "access_token": tokens["AuthenticationResult"]["AccessToken"],
            "refresh_token": tokens["AuthenticationResult"]["RefreshToken"],
            "expires_in": tokens["AuthenticationResult"]["ExpiresIn"],
            "token_type": tokens["AuthenticationResult"]["TokenType"],
        },
    )


@router.post("/register_user_face", status_code=status.HTTP_201_CREATED)
@protected_route
async def register_user_face(
    registration_service: RegistrationServiceDependency,
    current_user: CurrentUserDependency,
    image: UploadFile = File(...),
) -> JSONResponse:
    """Associate a user's face with their account."""
    image_bytes = await image.read()
    response = await registration_service.register_user_face(
        current_user.email, image_bytes
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": response["message"],
        },
    )


@router.post("/verify_face", status_code=status.HTTP_200_OK)
@protected_route
async def verify_face(
    registration_service: RegistrationServiceDependency,
    current_user: CurrentUserDependency,
    image: UploadFile = File(...),
) -> JSONResponse:
    image_bytes = await image.read()
    await registration_service.verify_face(current_user.email, image_bytes)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Face verified successfully"},
    )
