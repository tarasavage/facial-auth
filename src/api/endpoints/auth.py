from fastapi import APIRouter
from src.services.token import CognitoTokenServiceDependency


router = APIRouter()

@router.post("/token")
async def token(username: str, password: str, token_service: CognitoTokenServiceDependency):
    token = token_service.generate_tokens(username, password)
    return {"token": token}
