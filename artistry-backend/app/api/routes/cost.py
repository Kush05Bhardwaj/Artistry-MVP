from fastapi import APIRouter
from app.services.cost_estimation import estimate_cost

router = APIRouter(prefix="/cost")

@router.post("/")
def cost(room_analysis: dict):
    return {"cost_estimate": estimate_cost(room_analysis)}
