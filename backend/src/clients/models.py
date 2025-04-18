from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel, String, Column

if TYPE_CHECKING:
    from users.models import User


class ClientUserLink(SQLModel, table=True):
    __tablename__ = "client_users"

    client_id: int = Field(default=None, foreign_key="clients.id", primary_key=True)
    user_id: int = Field(default=None, foreign_key="users.id", primary_key=True)


class Client(SQLModel, table=True):
    __tablename__ = "clients"

    id: int = Field(default=None, primary_key=True)
    login_redirect_url: str = Field(sa_column=Column(String))
    logout_redirect_url: str = Field(sa_column=Column(String))
    domain: str = Field(sa_column=Column(String, unique=True))
    client_id: str = Field(sa_column=Column(String, unique=True))

    owner_id: int = Field(foreign_key="users.id")
    owner: "User" = Relationship(back_populates="clients")

    users: list["User"] = Relationship(back_populates="clients", link_model=ClientUserLink)

    class Config:
        from_attributes = True
