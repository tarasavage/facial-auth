from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from registration.routes import router as registration_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(users_router, prefix="/users")
# app.include_router(auth_router, prefix="")
# app.include_router(rekognition_router, prefix="")

app.include_router(registration_router, prefix="/registration")


@app.get("/")
async def root():
    return "Welcome!"


@app.get("/health")
async def health():
    return {"status": "ok"}
