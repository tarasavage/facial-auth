from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text

from core.config import Settings, get_settings
from core.db import engine


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    return {"status": "ok"}
