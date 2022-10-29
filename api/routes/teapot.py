from fastapi import APIRouter

router = APIRouter()


@router.get("/teapot", status_code=418)
def teapot(): # ☕
    """
    Error response code indicates that the server refuses to brew coffee because it is, permanently, a teapot.
    """  # noqa: E501
    return "I'm a teapot"
