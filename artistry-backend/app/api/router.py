from fastapi import APIRouter
from app.api.routes import analysis, decor, visualize, cost, diy, save

api_router = APIRouter(prefix="/api")

api_router.include_router(analysis.router, tags=["Room Analysis"])
api_router.include_router(decor.router, tags=["Decor Suggestions"])
api_router.include_router(visualize.router, tags=["Before After"])
api_router.include_router(cost.router, tags=["Cost Estimation"])
api_router.include_router(diy.router, tags=["DIY Guidance"])
api_router.include_router(save.router, tags=["Save & Share"])
