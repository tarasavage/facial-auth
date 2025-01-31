import abc
import base64
import hashlib
import hmac
from typing import Annotated

import boto3
from fastapi.params import Depends

from core.config import Settings, SettingsDependency


class TokenRepo(abc.ABC):
    @abc.abstractmethod
    def generate_tokens(self, user: str, pwd: str) -> str:
        pass

    @abc.abstractmethod
    def verify_token(self, token: str) -> bool:
        pass

    @abc.abstractmethod
    def refresh_token(self, token: str) -> str:
        pass

    @abc.abstractmethod
    def revoke_token(self, token: str) -> None:
        pass


class CognitoRepo(TokenRepo):
    def __init__(self, settings: Settings):
        self.cfg = settings
        self.cognito_idp_client = boto3.client(
            "cognito-idp",
            region_name=self.cfg.AWS_REGION,
            aws_access_key_id=self.cfg.AWS_ACCESS_KEY,
            aws_secret_access_key=self.cfg.AWS_SECRET_ACCESS_KEY,
        )

    def generate_tokens(self, user: str, pwd: str) -> str:
        kwargs = {
            "AuthFlow": "ADMIN_USER_PASSWORD_AUTH",
            "AuthParameters": {
                "USERNAME": user,
                "PASSWORD": pwd,
                "SECRET_HASH": self._calculate_secret_hash(user),
            },
            "ClientId": self.cfg.AWS_COGNITO_CLIENT_ID,
            "UserPoolId": self.cfg.AWS_COGNITO_USER_POOL_ID,
        }

        resp = self.cognito_idp_client.admin_initiate_auth(**kwargs)
        return resp

    def verify_token(self, token: str) -> bool:
        pass

    def refresh_token(self, token: str) -> str:
        pass

    def revoke_token(self, token: str) -> None:
        pass

    def _calculate_secret_hash(self, username: str) -> str:
        msg = username + self.cfg.AWS_COGNITO_CLIENT_ID
        message = bytes(msg, 'utf-8')
        key = bytes(self.cfg.AWS_COGNITO_CLIENT_SECRET, 'utf-8')
        return base64.b64encode(
            hmac.new(key, message, digestmod=hashlib.sha256).digest()
        ).decode()


def get_cognito_repo(settings: SettingsDependency) -> TokenRepo:
    """Provide TokenRepo instance"""
    return CognitoRepo(settings)


CognitoRepoDependency = Annotated[TokenRepo, Depends(get_cognito_repo)]
