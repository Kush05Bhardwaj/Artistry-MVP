from fastapi import APIRouter
from app.services.decor_suggestions import generate_decor

router = APIRouter(prefix="/decor")

@router.post("/")
def decor(room_analysis: dict):
    return {"decor_suggestions": generate_decor(room_analysis)}
