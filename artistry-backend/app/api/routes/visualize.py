from fastapi import APIRouter
from app.services.visualization import generate_before_after

router = APIRouter(prefix="/visualize")

@router.post("/")
def visualize(image_path: str):
    return generate_before_after(image_path)
