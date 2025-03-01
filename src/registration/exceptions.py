class ServiceError(Exception):
    pass

class FaceVerificationNotEnabledError(ServiceError):
    """Raised when face verification is not enabled for a user"""
    pass
