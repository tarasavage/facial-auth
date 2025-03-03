from pydantic import BaseModel, EmailStr


class UserSignInCredentials(BaseModel):
    email: EmailStr
    password: str
