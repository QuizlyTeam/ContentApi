from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from firebase_admin import db
from firebase_admin.exceptions import FirebaseError

from ..dependencies import get_user_token
from ..schemas.users import CreateUserAccount, UserAccount

router = APIRouter()


@router.post(
    "/",
    response_model=UserAccount,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                        "name": "Alan Turing",
                        "nickname": "turingComplete",
                        "picture": "http://t2.gstatic.com/licensed-image?q=tbn:ANd9GcQCUUTlwrAsh5cZ9yds4YIELmAgLT-kyXXJ7vhrzQLriwYb3VQqSTToKpq7heaNcMZX",  # noqa
                        "win": 0,
                        "lose": 0,
                        "favourite_category": "-",
                        "max_points": 0,
                    }
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "content": {
                "application/json": {
                    "example": {"detail": "Bearer authentication is needed"}
                }
            }
        },
        status.HTTP_409_CONFLICT: {
            "content": {
                "application/json": {
                    "example": {"detail": "Account already exists"}
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {},
    },
)
async def post_user(body: CreateUserAccount, user=Depends(get_user_token)):
    """
    Create a user account.
    """
    userAccount = UserAccount(
        **{
            "uid": user["uid"],
            "name": user["name"],
            "nickname": body.nickname,
            "picture": user["picture"],
            "win": 0,
            "lose": 0,
            "favourite_category": "-",
            "max_points": 0,
        }
    )
    try:
        ref = db.reference("Users")
        if (
            ref.order_by_child("uid")
            .equal_to(userAccount.uid)
            .limit_to_first(1)
            .get()
            is not None
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account already exists",
            )
        if (
            ref.order_by_child("nickname")
            .equal_to(userAccount.nickname)
            .limit_to_first(1)
            .get()
            is not None
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Nickname {userAccount.nickname} was already taken",
            )
        ref.push().set(userAccount.dict())
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(userAccount),
        )
    except FirebaseError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get(
    "/",
    response_model=UserAccount,
    responses={
        status.HTTP_200_OK: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                        "name": "Alan Turing",
                        "nickname": "turingComplete",
                        "picture": "http://t2.gstatic.com/licensed-image?q=tbn:ANd9GcQCUUTlwrAsh5cZ9yds4YIELmAgLT-kyXXJ7vhrzQLriwYb3VQqSTToKpq7heaNcMZX",  # noqa
                        "win": 0,
                        "lose": 0,
                        "favourite_category": "-",
                        "max_points": 0,
                    }
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "content": {
                "application/json": {
                    "example": {"detail": "Bearer authentication is needed"}
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "content": {
                "application/json": {
                    "example": {"detail": "User cannot be found"}
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {},
    },
)
async def get_user(user=Depends(get_user_token)):
    """
    Get user details.
    """
    try:
        ref = db.reference("Users")
        user_details = (
            ref.order_by_child("uid")
            .equal_to(user["uid"])
            .limit_to_first(1)
            .get()
        )
        if user_details is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User cannot be found",
            )
        else:
            return JSONResponse(
                content=jsonable_encoder(next(iter(user_details.items()))[1])
            )
    except FirebaseError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
