from fastapi import FastAPI
from api.endpoints.auth import router as auth_router
from users.router import router as users_router
from core.config import get_settings

app = FastAPI()

app.include_router(users_router, prefix="/users")
app.include_router(auth_router, prefix="/auth")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    return {"status": "ok"}
