from typing import TYPE_CHECKING

from sqlmodel import Column, Field, Relationship, SQLModel, String

from clients.models import ClientUserLink

if TYPE_CHECKING:
    from clients.models import Client


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column(String, unique=True))
    email: str = Field(sa_column=Column(String, unique=True))
    face_image_key: str | None = Field(sa_column=Column(String, unique=True))
    email_verified: bool = Field(default=False, sa_column_kwargs={"server_default": "false"})
    is_direct: bool = Field(default=True, sa_column_kwargs={"server_default": "true"})

    clients: list["Client"] | None = Relationship(back_populates="users", link_model=ClientUserLink)

    @property
    def s3_face_image_key(self) -> str:
        return f"face_{self.id}.jpg"
