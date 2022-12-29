from fastapi import APIRouter

from ..constants.tags import Tags
from .quizzes import router as quizzes_router
from .users import router as users_router

main_router = APIRouter(prefix="/v1")

main_router.include_router(
    quizzes_router, prefix="/quizzes", tags=[Tags.quizzes]
)

main_router.include_router(
    users_router, prefix="/users", tags=[Tags.users]
)
