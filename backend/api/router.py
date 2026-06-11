from fastapi import APIRouter
from modules.user.router import router as user_router
from modules.generate.router import router as generate_router
from modules.history.router import router as history_router
from modules.mypage.router import router as mypage_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/auth", tags=["auth"])
api_router.include_router(generate_router, prefix="/generate", tags=["generate"])
api_router.include_router(history_router, prefix="/history", tags=["history"])
api_router.include_router(mypage_router, prefix="/mypage", tags=["mypage"])