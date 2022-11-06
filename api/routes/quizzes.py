from fastapi import APIRouter, status
from requests import get

from ..config import settings
from ..schemas.quizzes import CategoriesModel

router = APIRouter()


@router.get(
    "/categories",
    response_model=CategoriesModel,
    responses={
        status.HTTP_200_OK: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "categories": ["Arts & Literature", "Film & TV"]
                    }
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Something went wrong"
        },
    },
)
async def get_categories():
    """
    Get quiz categories.
    """
    result = get(f"{settings.server.quiz_api}/categories")
    categories = list(result.json().keys())

    return {"categories": categories}
