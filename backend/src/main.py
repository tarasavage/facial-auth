import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from clients.routes import router as clients_router
from core.config import get_settings
from core.tags import tags_metadata, Tags
from registration.routes import router as registration_router

app = FastAPI(
    title="Authentication API",
    description="API for handling user authentication and registration",
    openapi_tags=tags_metadata,
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
)

app.include_router(registration_router, prefix="/registration")
app.include_router(clients_router, prefix="/clients")


@app.get("/")
async def root():
    return "Welcome!"


@app.get("/health", tags=[Tags.HEALTH])
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
