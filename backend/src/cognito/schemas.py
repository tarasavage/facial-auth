from pydantic import BaseModel, EmailStr


class Profile(BaseModel):
    sub: str
    username: str
    email: EmailStr
    email_verified: bool
