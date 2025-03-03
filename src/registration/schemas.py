from pydantic import BaseModel, EmailStr


class UserSignInCredentials(BaseModel):
    email: EmailStr
    password: str


class UserConfirmSignupCredentials(BaseModel):
    email: EmailStr
    code: str
