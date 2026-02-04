from fastapi import APIRouter
from app.services.decor_suggestions import suggest_decor

router = APIRouter(prefix="/decor")

@router.post("/")
def decor(objects: list):
    return {"suggestions": suggest_decor(objects)}
