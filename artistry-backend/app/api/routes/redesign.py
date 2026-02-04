from fastapi import APIRouter, UploadFile, File
import shutil
from app.services.room_redesign_pipeline import redesign_room
from app.core.config import UPLOAD_DIR

router = APIRouter(prefix="/redesign")

@router.post("/")
async def redesign(file: UploadFile = File(...)):
    path = f"{UPLOAD_DIR}/{file.filename}"

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return redesign_room(path)
