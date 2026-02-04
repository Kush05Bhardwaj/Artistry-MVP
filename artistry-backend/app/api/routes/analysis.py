from fastapi import APIRouter, UploadFile, File
import shutil
from app.services.room_analysis import analyze_room
from app.core.config import UPLOAD_DIR

router = APIRouter(prefix="/analyze")

@router.post("/")
async def analyze(file: UploadFile = File(...)):
    path = f"{UPLOAD_DIR}/{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return analyze_room(path)
