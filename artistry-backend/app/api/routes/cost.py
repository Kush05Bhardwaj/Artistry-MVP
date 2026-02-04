from fastapi import APIRouter
from app.services.cost_estimation import estimate_cost

router = APIRouter(prefix="/cost")

@router.post("/")
def cost(objects: list):
    return estimate_cost(objects)
