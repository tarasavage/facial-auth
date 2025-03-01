from typing import Annotated, Optional
import boto3
from fastapi import Depends
from botocore.exceptions import ClientError

from auth.utils import calculate_secret_hash
from core.config import SettingsDependency
from auth.exceptions import PasswordValidationError

class CognitoRepo:
    """Repository class for AWS Cognito operations"""

    def __init__(
        self,
        user_pool_id: str,
        client_id: str,
        client_secret: str,
        aws_region: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ):
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.client_secret = client_secret

        self._cognito_idp = boto3.client(
            "cognito-idp",
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    def _secret_hash(self, user: str) -> str:
        return calculate_secret_hash(user, self.client_id, self.client_secret)

    def signup(self, user: str, pwd: str) -> dict:
        """Register a new user in Cognito"""
        try:
            response = self._cognito_idp.sign_up(
                ClientId=self.client_id,
                Username=user,
                Password=pwd,
                UserAttributes=[{"Name": "email", "Value": user}],
                SecretHash=self._secret_hash(user),
            )
            return response
        except self._cognito_idp.exceptions.InvalidPasswordException as e:
            error_message = e.response.get('Error', {}).get('Message', str(e))
            raise PasswordValidationError(error_message) from e
        except ClientError as e:
            raise e

    def confirm_signup(self, user: str, code: str) -> dict:
        """Confirm user registration with verification code"""
        try:
            response = self._cognito_idp.confirm_sign_up(
                ClientId=self.client_id,
                Username=user,
                ConfirmationCode=code,
                SecretHash=self._secret_hash(user),
            )
            return response
        except ClientError as e:
            raise e

    def signin(self, user: str, pwd: str) -> dict:
        """Authenticate user and return tokens"""
        try:
            response = self._cognito_idp.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": user,
                    "PASSWORD": pwd,
                    "SECRET_HASH": self._secret_hash(user),
                },
            )
            return response
        except ClientError as e:
            raise e

    def logout(self, access_token: str) -> dict:
        """Global sign out user"""
        try:
            response = self._cognito_idp.global_sign_out(AccessToken=access_token)
            return response
        except ClientError as e:
            raise e

    def get_user_profile(self, access_token: str) -> dict:
        """Get user profile information"""
        try:
            response = self._cognito_idp.get_user(AccessToken=access_token)
            user_attrs = {
                attr["Name"]: attr["Value"] for attr in response["UserAttributes"]
            }
            return {"username": response["Username"], "attributes": user_attrs}
        except ClientError as e:
            raise e

    def change_password(
        self, access_token: str, old_password: str, new_password: str
    ) -> dict:
        """Change user password"""
        try:
            response = self._cognito_idp.change_password(
                AccessToken=access_token,
                PreviousPassword=old_password,
                ProposedPassword=new_password,
            )
            return response
        except ClientError as e:
            raise e

    def forgot_password(self, username: str) -> dict:
        """Initiate forgot password flow"""
        try:
            response = self._cognito_idp.forgot_password(
                ClientId=self.client_id, Username=username
            )
            return response
        except ClientError as e:
            raise e

    def confirm_forgot_password(
        self, username: str, code: str, new_password: str
    ) -> dict:
        """Complete forgot password flow"""
        try:
            response = self._cognito_idp.confirm_forgot_password(
                ClientId=self.client_id,
                Username=username,
                ConfirmationCode=code,
                Password=new_password,
            )
            return response
        except ClientError as e:
            raise e


def get_cognito_repo(settings: SettingsDependency) -> CognitoRepo:
    """Dependency injection for CognitoRepo"""
    return CognitoRepo(
        user_pool_id=settings.AWS_COGNITO_USER_POOL_ID,
        client_id=settings.AWS_COGNITO_CLIENT_ID,
        client_secret=settings.AWS_COGNITO_CLIENT_SECRET,
        aws_region=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


CognitoRepoDependency = Annotated[CognitoRepo, Depends(get_cognito_repo)]