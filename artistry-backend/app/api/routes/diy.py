from fastapi import APIRouter
from app.services.diy_guidance import diy_steps

router = APIRouter(prefix="/diy")

@router.post("/")
def diy(objects: list):
    return {"steps": diy_steps(objects)}
