import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from registration.routes import router as registration_router

app = FastAPI()

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
)

app.include_router(registration_router, prefix="/registration")


@app.get("/")
async def root():
    return "Welcome!"


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ssl_keyfile="ssl/key.pem",
        ssl_certfile="ssl/cert.pem",
    )
