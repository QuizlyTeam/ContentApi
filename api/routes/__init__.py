from fastapi import APIRouter

from ..constants.tags import Tags
from .quizzes import router as quizzes_router
from .users import router as users_router

"""
The main router for the API. This is the main function that is called when the server is started.
:param prefix: - the prefix for the API. This is the first part of the URL.
:return: the main router
"""
main_router = APIRouter(prefix="/v1")

"""
Include the quizzes router in the main router. This router will handle all requests for the quizzes.
:param quizzes_router: - the quizzes router
:param prefix: - the prefix for the quizzes router
:param tags: - the tags for the quizzes router
"""
main_router.include_router(
    quizzes_router, prefix="/quizzes", tags=[Tags.quizzes]
)

"""
Include the users router in the main router. This is used to create a new user and get detail info about user.
:param users_router: - the users router
:param prefix: - the prefix for the users router
:param tags: - the tags for the users router
"""
main_router.include_router(users_router, prefix="/users", tags=[Tags.users])
