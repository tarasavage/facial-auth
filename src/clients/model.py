from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from users.model import User


class Client(SQLModel, table=True):
    __tablename__ = "clients"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String))
    service_id: int = Field(sa_column=Column(Integer))

    user_id: int = Field(sa_column=Column(ForeignKey("users.id")))
    user: User = Relationship(back_populates="clients")

