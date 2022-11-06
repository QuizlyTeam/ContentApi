from fastapi import APIRouter

from ..constants.tags import Tags
from .quizzes import router as quizzes_router

main_router = APIRouter(prefix="/v1")

main_router.include_router(
    quizzes_router, prefix="/quizzes", tags=[Tags.quizzes]
)
