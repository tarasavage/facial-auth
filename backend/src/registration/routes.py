from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from cognito.user_dependency import CurrentUserDependency
from registration.decorators import protected_route
from registration.dependencies import UserFromCookieDependency, PERSON_IDENTITY_COOKIE_NAME
from registration.exceptions import ServiceError
from registration.schemas import (
    UserConfirmSignupCredentials,
    UserSignInCredentials,
)
from registration.service import RegistrationServiceDependency
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
        await registration_service.confirm_signup(email=confirm_signup_data.email, code=confirm_signup_data.code)
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
    """Authenticate user and return access tokens with HTTPOnly cookie."""
    unauthorized_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )

    try:
        credentials = await registration_service.perform_user_signin_flow(signin_data.email, signin_data.password)
    except ServiceError as e:
        raise unauthorized_error from e

    resp = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": credentials.message,
            "access_token": credentials.access_token,
            "refresh_token": credentials.refresh_token,
            "expires_in": credentials.expires_in,
            "token_type": credentials.token_type,
        },
    )

    if credentials.cookie is not None:
        resp.set_cookie(
            key=PERSON_IDENTITY_COOKIE_NAME,
            value=f"Bearer {credentials.cookie}",
            httponly=True,
            secure=True,
        )

    return resp


@router.post("/register_user_face", status_code=status.HTTP_201_CREATED)
@protected_route
async def register_user_face(
    registration_service: RegistrationServiceDependency,
    current_user: CurrentUserDependency,
    image: UploadFile = File(...),
) -> JSONResponse:
    """Associate a user's face with their account with HTTPOnly cookie."""
    image_bytes = await image.read()
    service_response = await registration_service.register_face_and_issue_token(current_user.email, image_bytes)

    response = JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": service_response.message})
    response.set_cookie(
        key=PERSON_IDENTITY_COOKIE_NAME,
        value=f"Bearer {service_response.token}",
        httponly=True,
        secure=True,
    )
    return response


@router.post("/signin_via_face", status_code=status.HTTP_200_OK)
async def signin_via_face(
    registration_service: RegistrationServiceDependency,
    user_from_cookie: UserFromCookieDependency,
    image: UploadFile = File(...),
) -> JSONResponse:
    image_bytes = await image.read()
    credentials = await registration_service.signin_via_face(user_from_cookie.email, image_bytes)

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "access_token": credentials.access_token,
            "refresh_token": credentials.refresh_token,
            "expires_in": credentials.expires_in,
            "token_type": credentials.token_type,
        },
    )

    response.set_cookie(
        key=PERSON_IDENTITY_COOKIE_NAME,
        value=f"Bearer {credentials.cookie}",
        httponly=True,
        secure=True,
    )
    return response


@router.post("/verify_face", status_code=status.HTTP_200_OK)
@protected_route
async def verify_face(
    registration_service: RegistrationServiceDependency,
    current_user: CurrentUserDependency,
    image: UploadFile = File(...),
) -> JSONResponse:
    if not current_user.email_verified:
        raise HTTPException(status_code=400, detail="Email not verified")

    image_bytes = await image.read()
    await registration_service.verify_face(current_user.email, image_bytes)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True, "message": "Face verified successfully"})


@router.get("/me", status_code=status.HTTP_200_OK)
@protected_route
async def get_user_profile(
    registration_service: RegistrationServiceDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    user_profile = await registration_service.get_user_profile(current_user.email)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True, "data": user_profile})


@router.post("/check_face_auth", status_code=status.HTTP_200_OK)
async def check_face_auth(
    user_from_cookie: UserFromCookieDependency,
    registration_service: RegistrationServiceDependency,
) -> JSONResponse:
    """Check if user has a valid identity cookie for face authentication."""
    if user_from_cookie and user_from_cookie.email:
        has_face_registered = await registration_service.check_if_face_auth_is_enabled(user_from_cookie.email)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"can_use_face_auth": has_face_registered, "email": user_from_cookie.email},
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"can_use_face_auth": False, "success": True})
