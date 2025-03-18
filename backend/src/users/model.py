from sqlmodel import Column, Field, SQLModel, String


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column(String, unique=True))
    email: str = Field(sa_column=Column(String, unique=True))
    face_image_key: str | None = Field(sa_column=Column(String, unique=True))
    email_verified: bool = Field(default=False, sa_column_kwargs={"server_default": "false"})

    @property
    def s3_face_image_key(self) -> str:
        return f"face_{self.id}.jpg"
