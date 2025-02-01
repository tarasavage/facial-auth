from fastapi import Depends
from typing_extensions import Annotated

from token_provider.token_repo import CognitoRepoDependency, TokenRepo


class TokenService:
    def __init__(self, token_provider: TokenRepo):
        self.token_provider = token_provider

    def generate_tokens(self, username: str, password: str) -> str:
        return self.token_provider.generate_tokens(username, password)

    def verify_token(self, token: str) -> bool:
        return self.token_provider.verify_token(token)

    def refresh_token(self, token: str) -> str:
        return self.token_provider.refresh_token(token)


def get_cognito_token_service(token_provider: CognitoRepoDependency) -> TokenService:
    return TokenService(token_provider)


CognitoTokenServiceDependency = Annotated[
    TokenService, Depends(get_cognito_token_service)
]
