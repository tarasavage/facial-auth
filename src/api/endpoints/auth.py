from fastapi import APIRouter

from token_provider.token_service import CognitoTokenServiceDependency


router = APIRouter()


@router.post("/token")
async def token(
    username: str, password: str, token_service: CognitoTokenServiceDependency
):
    token = token_service.generate_tokens(username, password)
    return {"token": token}
