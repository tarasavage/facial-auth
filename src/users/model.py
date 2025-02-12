from sqlmodel import Column, Field, SQLModel, String


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column(String, unique=True))
    email: str = Field(sa_column=Column(String, unique=True))
    password: str = Field(sa_column=Column(String))
