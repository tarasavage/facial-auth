class RekognitionError(Exception):
    """Base exception for all Rekognition-related operations."""


class RekognitionClientError(RekognitionError):
    """Exception raised when Rekognition client initialization fails."""


class FaceImageValidationError(RekognitionError):
    """Exception raised when face image validation fails."""


class RekognitionLimitExceededError(RekognitionError):
    """Exception raised when Rekognition limits are exceeded."""


class MultipleFacesDetectedError(RekognitionError):
    """Exception raised when multiple faces are detected."""


class FaceValidationError(RekognitionError):
    """Base exception for face validation errors."""


class InvalidFaceCountError(FaceValidationError):
    """Exception raised when the number of faces detected is invalid."""


class FaceOccludedError(FaceValidationError):
    """Exception raised when the face is occluded."""


class SunglassesError(FaceValidationError):
    """Exception raised when the face is wearing sunglasses."""


class InvalidS3ObjectError(RekognitionError):
    """Exception raised when the S3 object is invalid or cannot be fetched."""
