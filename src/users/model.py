from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from clients.model import Client


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column(String, unique=True))
    email: str = Field(sa_column=Column(String, unique=True))
    password: str = Field(sa_column=Column(String))

    clients: List["Client"] = Relationship(back_populates="user")

