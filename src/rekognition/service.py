from typing import Annotated

from fastapi import Depends
from rekognition.repository import (
    RekognitionRepository,
    RekognitionRepositoryDependency,
)


class RekognitionService:
    """Orchestrates face comparison operations with proper validation and error handling."""

    def __init__(self, repo: RekognitionRepository) -> None:
        self._repo = repo
        self._threshold = 95.0

    def compare_faces(self, source_image: bytes, target_image: bytes) -> list[dict]:
        resp = self._repo.compare_faces(source_image, target_image, self._threshold)
        return self._format_matches(resp["FaceMatches"], self._threshold)

    def _format_matches(self, matches: list[dict], threshold) -> list[dict]:
        return [
            {
                "Similarity": match["Similarity"],
                "Matched": match["Similarity"] >= threshold,
            }
            for match in matches
        ]


def get_rekognition_service(
    repo: RekognitionRepositoryDependency,
) -> RekognitionService:
    return RekognitionService(repo)


RekognitionServiceDependency = Annotated[
    RekognitionService, Depends(get_rekognition_service)
]
