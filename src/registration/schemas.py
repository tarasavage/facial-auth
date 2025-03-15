from pydantic import BaseModel, EmailStr

from tokens.schemas import TokenData


class CookieProfile(BaseModel):
    email: EmailStr
    sub: str


class UserSignInCredentials(BaseModel):
    email: EmailStr
    password: str


class UserConfirmSignupCredentials(BaseModel):
    email: EmailStr
    code: str


class FaceRegistrationResult(BaseModel):
    status: str
    message: str
    data: dict

    @classmethod
    def success(cls, message: str, data: dict) -> "FaceRegistrationResult":
        return cls(status="success", message=message, data=data)

    @classmethod
    def error(cls, message: str) -> "FaceRegistrationResult":
        return cls(status="error", message=message, data={})


class RegisterUserFaceResponse(TokenData):
    message: str


class SignInViaFaceResponse(TokenData):
    message: str
