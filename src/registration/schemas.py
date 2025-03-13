from pydantic import BaseModel, EmailStr


class UserSignInCredentials(BaseModel):
    email: EmailStr
    password: str


class UserConfirmSignupCredentials(BaseModel):
    email: EmailStr
    code: str


class RegisterUserFaceResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    expires_in: int
