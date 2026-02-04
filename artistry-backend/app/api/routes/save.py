from fastapi import APIRouter
from app.services.storage import save_design

router = APIRouter(prefix="/save")

@router.post("/")
def save(data: dict):
    return {"saved_to": save_design(data)}
