from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.ppt import router as ppt_router
from app.api.template import router as template_router
from app.api.payment import router as payment_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(ppt_router)
api_router.include_router(template_router)
api_router.include_router(payment_router)
