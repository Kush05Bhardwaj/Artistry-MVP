from fastapi import APIRouter, UploadFile, File
from app.services.room_analysis import analyze_room
import shutil

router = APIRouter(prefix="/analyze")

@router.post("/")
async def analyze_room_api(file: UploadFile = File(...)):
    path = f"temp/{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return analyze_room(path)
