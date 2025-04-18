from pydantic import BaseModel, EmailStr


class CookieProfile(BaseModel):
    email: EmailStr


class UserSignInCredentials(BaseModel):
    email: EmailStr
    password: str


class UserConfirmSignupCredentials(BaseModel):
    email: EmailStr
    code: str


class FaceRegistrationResult(BaseModel):
    status: str
    message: str

    @classmethod
    def success(cls, message: str) -> "FaceRegistrationResult":
        return cls(status="success", message=message)

    @classmethod
    def error(cls, message: str) -> "FaceRegistrationResult":
        return cls(status="error", message=message)


class UserProfileResponse(BaseModel):
    email: EmailStr
    username: str
    is_direct: bool = True


class RegisterUserFaceResponse(BaseModel):
    message: str
    cookie: str
    expires_in: int


class SignInResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str
