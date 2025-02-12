import abc
from typing import Annotated

import boto3
from fastapi.params import Depends

from core.config import Settings, SettingsDependency
from auth.utils import calculate_secret_hash


class TokenRepo(abc.ABC):
    ...
    # @abc.abstractmethod
    # def generate_tokens(self, user: str, pwd: str) -> str:
    #     pass

    # @abc.abstractmethod
    # def verify_token(self, token: str) -> bool:
    #     pass

    # @abc.abstractmethod
    # def refresh_token(self, token: str) -> str:
    #     pass

    # @abc.abstractmethod
    # def revoke_token(self, token: str) -> None:
    #     pass


class CognitoRepo(TokenRepo):
    def __init__(self, settings: Settings):
        self.cfg = settings
        self.client = boto3.client(
            "cognito-idp",
            region_name=self.cfg.AWS_REGION,
            aws_access_key_id=self.cfg.AWS_ACCESS_KEY,
            aws_secret_access_key=self.cfg.AWS_SECRET_ACCESS_KEY,
        )

    @property
    def _user_pool_id(self) -> str:
        return self.cfg.AWS_COGNITO_USER_POOL_ID

    @property
    def _client_id(self) -> str:
        return self.cfg.AWS_COGNITO_CLIENT_ID

    @property
    def _client_secret(self) -> str:
        return self.cfg.AWS_COGNITO_CLIENT_SECRET

    def _secret_hash(self, user: str) -> str:
        return calculate_secret_hash(
            user, self.cfg.AWS_COGNITO_CLIENT_ID, self.cfg.AWS_COGNITO_CLIENT_SECRET
        )

    def signin(self, user: str, pwd: str) -> dict:
        hash = self._secret_hash(user)
        kwargs = {
            "AuthFlow": "USER_PASSWORD_AUTH",
            "AuthParameters": {
                "USERNAME": user,
                "PASSWORD": pwd,
                "SECRET_HASH": hash,
            },
            "ClientId": self._client_id,
        }
        resp = self.client.initiate_auth(**kwargs)

        return resp

    def signup(self, user: str, pwd: str) -> dict:
        kwargs = {
            "ClientId": self._client_id,
            "Username": user,
            "Password": pwd,
            "SecretHash": self._secret_hash(user),
            "UserAttributes": [
                {
                    "Name": "email",
                    "Value": user,
                }
            ],
        }
        return self.client.sign_up(**kwargs)

    def confirm_signup(self, user: str, code: str) -> dict:
        kwargs = {
            "ClientId": self._client_id,
            "SecretHash": self._secret_hash(user),
            "Username": user,
            "ConfirmationCode": code,
        }
        return self.client.confirm_sign_up(**kwargs)

    def logout(self, token: str) -> dict:
        # TODO: validate behavior
        kwargs = {
            "AccessToken": token,
        }
        return self.client.global_sign_out(**kwargs)


def get_cognito_repo(settings: SettingsDependency) -> TokenRepo:
    """Provide TokenRepo instance"""
    return CognitoRepo(settings)


CognitoRepoDependency = Annotated[TokenRepo, Depends(get_cognito_repo)]
