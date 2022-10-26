from fastapi import APIRouter

from .teapot import router as teapot_router

main_router = APIRouter()

main_router.include_router(teapot_router)


@main_router.get("/")
async def index():
    return {"message": "Hello World!"}
