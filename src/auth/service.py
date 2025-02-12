from fastapi import Depends
from typing_extensions import Annotated

from auth.repository import CognitoRepoDependency, TokenRepo


class TokenService:
    def __init__(self, token_provider: TokenRepo):
        self.token_provider = token_provider

    def signin(self, user: str, pwd: str) -> dict:
        return self.token_provider.signin(user, pwd)

    def signup(self, user: str, pwd: str) -> dict:
        return self.token_provider.signup(user, pwd)

    def confirm_signup(self, user: str, code: str) -> dict:
        return self.token_provider.confirm_signup(user, code)

    def logout(self, token: str) -> dict:
        return self.token_provider.logout(token)
        


def get_cognito_token_service(token_provider: CognitoRepoDependency) -> TokenService:
    return TokenService(token_provider)


CognitoTokenServiceDependency = Annotated[
    TokenService, Depends(get_cognito_token_service)
]
