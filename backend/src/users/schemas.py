from typing import Optional

from pydantic import ConfigDict, EmailStr
from sqlmodel import SQLModel


class BaseUser(SQLModel):
    email: EmailStr
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseUser):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CreateUser(BaseUser):
    password: str


class CreateNonDirectUser(BaseUser):
    password: str
    client_id: str


class UpdateUser(SQLModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    face_image_key: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
