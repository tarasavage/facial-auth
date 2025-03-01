class AuthError(Exception):
    """Base class for auth-related errors"""

    pass


class SignupError(AuthError):
    """Raised when signup fails"""

    pass


class SigninError(AuthError):
    """Raised when signin fails"""

    pass


class SignUpError(AuthError):
    """Raised when signup fails"""

    pass


class InvalidPasswordError(SignUpError):
    """Raised when the password is invalid"""

    pass


class PasswordValidationError(SignUpError):
    """Raised when password doesn't meet the requirements"""

    pass


class InvalidCodeError(SignUpError):
    """Raised when the code is invalid"""

    pass


class ConfirmSignupError(AuthError):
    """Raised when confirm signup fails"""

    pass


class ExpiredCodeError(ConfirmSignupError):
    """Raised when the code has expired"""

    pass


class NotAuthorizedError(AuthError):
    """Raised when the user is not authorized to perform an action"""

    pass
