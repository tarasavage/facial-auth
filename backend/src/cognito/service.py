from typing import Annotated
from fastapi import Depends
from botocore.exceptions import ClientError

from cognito.exceptions import (
    ConfirmSignupError,
    ExpiredCodeError,
    InvalidPasswordError,
    NotAuthorizedError,
    SignUpError,
)
from cognito.repository import CognitoRepoDependency


class CognitoTokenService:
    """Service layer for Cognito operations"""

    def __init__(self, repo: CognitoRepoDependency):
        self.repo = repo

    def signup(self, email: str, pwd: str) -> dict:
        """Register a new user"""
        try:
            return self.repo.signup(email, pwd)
        except ClientError as e:
            if e.response["Error"]["Code"] == "InvalidPasswordException":
                raise InvalidPasswordError(e.response["Error"]["Message"])
            if e.response["Error"]["Code"] == "UsernameExistsException":
                raise SignUpError("User already exists")
            raise SignUpError(f"Failed to sign up: {str(e)}")

    def confirm_signup(self, user: str, code: str) -> dict:
        """Confirm user registration"""
        try:
            return self.repo.confirm_signup(user, code)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ExpiredCodeException":
                raise ExpiredCodeError("Verification code has expired")
            if e.response["Error"]["Code"] == "CodeMismatchException":
                raise ConfirmSignupError("Invalid verification code")
            raise ConfirmSignupError(f"Failed to confirm signup: {str(e)}")

    def signin(self, email: str, pwd: str) -> dict:
        """Authenticate user and return tokens"""
        try:
            return self.repo.signin(email, pwd)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NotAuthorizedException":
                raise NotAuthorizedError("Invalid credentials")
            if e.response["Error"]["Code"] == "UserNotConfirmedException":
                raise NotAuthorizedError("User is not confirmed")
            raise NotAuthorizedError(f"Authentication failed: {str(e)}")

    def logout(self, access_token: str) -> dict:
        """Sign out user globally"""
        try:
            return self.repo.logout(access_token)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NotAuthorizedException":
                raise NotAuthorizedError("Invalid or expired token")
            raise NotAuthorizedError(f"Logout failed: {str(e)}")

    def get_user_profile(self, access_token: str) -> dict:
        """Get current user profile"""
        try:
            return self.repo.get_user_profile(access_token)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NotAuthorizedException":
                raise NotAuthorizedError("Token is invalid or expired")
            raise NotAuthorizedError(f"Failed to get user profile: {str(e)}")

    def change_password(self, access_token: str, old_password: str, new_password: str) -> dict:
        """Change user password"""
        try:
            return self.repo.change_password(access_token, old_password, new_password)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NotAuthorizedException":
                raise NotAuthorizedError("Invalid credentials or token")
            if e.response["Error"]["Code"] == "InvalidPasswordException":
                raise InvalidPasswordError(e.response["Error"]["Message"])
            raise NotAuthorizedError(f"Failed to change password: {str(e)}")

    def forgot_password(self, email: str) -> dict:
        """Initiate forgot password process"""
        try:
            return self.repo.forgot_password(email)
        except ClientError as e:
            if e.response["Error"]["Code"] == "UserNotFoundException":
                raise NotAuthorizedError("User not found")
            raise NotAuthorizedError(f"Failed to initiate password reset: {str(e)}")

    def confirm_forgot_password(self, email: str, code: str, new_password: str) -> dict:
        """Complete forgot password process"""
        try:
            return self.repo.confirm_forgot_password(email, code, new_password)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ExpiredCodeException":
                raise ExpiredCodeError("Reset code has expired")
            if e.response["Error"]["Code"] == "CodeMismatchException":
                raise ConfirmSignupError("Invalid reset code")
            if e.response["Error"]["Code"] == "InvalidPasswordException":
                raise InvalidPasswordError(e.response["Error"]["Message"])
            raise NotAuthorizedError(f"Failed to reset password: {str(e)}")

    def signin_via_face(self, email: str, image_bytes: bytes, answer: str) -> dict:
        """Authenticate user and return tokens"""
        try:
            response = self.repo.initiate_face_auth(email)
            return self.repo.respond_to_face_auth(
                email=email,
                challenge_name=response["ChallengeName"],
                session=response["Session"],
                answer=answer,
            )
        except ClientError as e:
            raise e


def get_cognito_token_service(repo: CognitoRepoDependency) -> CognitoTokenService:
    """Dependency injection for CognitoTokenService"""
    return CognitoTokenService(repo)


CognitoTokenServiceDependency = Annotated[CognitoTokenService, Depends(get_cognito_token_service)]
