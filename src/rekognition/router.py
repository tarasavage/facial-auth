from fastapi import APIRouter, UploadFile, File

from rekognition.service import RekognitionServiceDependency


router = APIRouter(prefix="/rekognition", tags=["rekognition"])


@router.post("/compare")
async def compare_faces(
    service: RekognitionServiceDependency,
    source_face_image: UploadFile = File(...),
    target_face_image: UploadFile = File(...),
):
    """Compare two faces"""
    source_image = await source_face_image.read()
    target_image = await target_face_image.read()
    return service.compare_faces(source_image, target_image)
