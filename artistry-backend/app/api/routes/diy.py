from fastapi import APIRouter
from app.services.diy_guidance import generate_diy

router = APIRouter(prefix="/diy")

@router.post("/")
def diy(room_analysis: dict):
    return {"diy_steps": generate_diy(room_analysis)}
