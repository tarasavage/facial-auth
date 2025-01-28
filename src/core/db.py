from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import Session
from core.config import get_settings
from typing import Annotated, Generator


connection_args = {}
engine = create_engine(
    get_settings().DATABASE_URI, connect_args=connection_args, echo=True
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDependency = Annotated[Session, Depends(get_session)]
