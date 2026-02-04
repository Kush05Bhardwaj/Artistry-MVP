from fastapi import APIRouter
from app.api.routes import analysis, decor, visualize, cost, diy, save, redesign

router = APIRouter(prefix="/api")

router.include_router(analysis.router)
router.include_router(decor.router)
router.include_router(visualize.router)
router.include_router(cost.router)
router.include_router(diy.router)
router.include_router(save.router)
router.include_router(redesign.router)

api_router = router
