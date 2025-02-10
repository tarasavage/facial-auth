from fastapi import FastAPI

from auth.router import router as auth_router
from users.router import router as users_router

app = FastAPI()

app.include_router(users_router, prefix="/users")
app.include_router(auth_router, prefix="")


@app.get("/")
async def root():
    return "Welcome!"


@app.get("/health")
async def health():
    return {"status": "ok"}
