from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from requests import get
from firebase_admin import db
from firebase_admin.exceptions import FirebaseError

from ..config import settings
from ..dependencies import get_user_token
from ..schemas.quizzes import CategoriesModel, TagsModel, UserQuiz, UserQuizzes, DeleteUserQuizzes, CreateUserQuiz, UpdateUserQuiz

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

    return JSONResponse(
            content=jsonable_encoder({"categories": categories}),
        )


@router.get(
    "/tags",
    response_model=TagsModel,
    responses={
        status.HTTP_200_OK: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {"tags": ["alcohol", "acting"]}
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Something went wrong"
        },
    },
)
async def get_tags():
    """
    Get tags.
    """
    result = get(f"{settings.server.quiz_api}/tags")
    tags = list(result.json())

    return JSONResponse(
            content=jsonable_encoder({"tags": tags}),
        )

@router.post(
    "/",
    response_model=UserQuiz,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "category": "History",
                        "difficulty": "easy",
                        "questions": [
                            {
                            "correct_answer": "in London in 1912",
                            "incorrect_answers": [
                                "in Manchester in 1901",
                                "in Oxford in 1924",
                                "in Cambridge in 1935"
                            ],
                            "question": "Where and when was Alan Turing born?"
                            },
                            {
                            "correct_answer": "a Turing Machine",
                            "incorrect_answers": [
                                "the Bombe",
                                "Church's Computer",
                                "the Manchester Mach I"
                            ],
                            "question": "Turing, while solving the Decision Problem, proposed a hypothetical computing machine, which we now call ___"
                            }
                        ],
                        "tags": "1910's",
                        "title": "The father of the computer",
                        "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
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
async def post_user_quiz(body: CreateUserQuiz, user=Depends(get_user_token)):
    """
    Create user quiz.
    """
    userQuiz = UserQuiz(
        **{
            "uid": user["uid"],
            **body.dict()
        }
    )
    try:
        if (
            db.reference("Users").order_by_child("uid")
            .equal_to(userQuiz.uid)
            .limit_to_first(1)
            .get()
            is None
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User cannot be found",
            )
        db.reference("Quizzes").push().set(userQuiz.dict())
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(userQuiz),
        )
    except FirebaseError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get(
    "/",
    response_model=UserQuizzes,
    responses={
        status.HTTP_200_OK: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "YYYYYYYYYYYYYYYYYYYY": {
                            "category": "History",
                            "difficulty": "easy",
                            "questions": [
                                {
                                "correct_answer": "in London in 1912",
                                "incorrect_answers": [
                                    "in Manchester in 1901",
                                    "in Oxford in 1924",
                                    "in Cambridge in 1935"
                                ],
                                "question": "Where and when was Alan Turing born?"
                                },
                                {
                                "correct_answer": "a Turing Machine",
                                "incorrect_answers": [
                                    "the Bombe",
                                    "Church's Computer",
                                    "the Manchester Mach I"
                                ],
                                "question": "Turing, while solving the Decision Problem, proposed a hypothetical computing machine, which we now call ___"
                                }
                            ],
                            "tags": "1910's",
                            "title": "The father of the computer",
                            "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
                        }
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
async def get_user_quizzes(user=Depends(get_user_token)):
    """
    Get all user quizzes.
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
            ref = db.reference("Quizzes")
            user_quizzes = ref.order_by_child("uid").equal_to(user["uid"]).get()
            return JSONResponse(
                content=jsonable_encoder(user_quizzes)
            )
    except FirebaseError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get(
    "/{quiz_id}",
    response_model=UserQuiz,
    responses={
        status.HTTP_200_OK: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "category": "History",
                        "difficulty": "easy",
                        "questions": [
                            {
                            "correct_answer": "in London in 1912",
                            "incorrect_answers": [
                                "in Manchester in 1901",
                                "in Oxford in 1924",
                                "in Cambridge in 1935"
                            ],
                            "question": "Where and when was Alan Turing born?"
                            },
                            {
                            "correct_answer": "a Turing Machine",
                            "incorrect_answers": [
                                "the Bombe",
                                "Church's Computer",
                                "the Manchester Mach I"
                            ],
                            "question": "Turing, while solving the Decision Problem, proposed a hypothetical computing machine, which we now call ___"
                            }
                        ],
                        "tags": "1910's",
                        "title": "The father of the computer",
                        "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
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
async def get_user_quiz(quiz_id: str, user=Depends(get_user_token)):
    """
    Get user quiz.
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
        ref = db.reference("Quizzes")
        user_quizzes = ref.order_by_child("uid").equal_to(user["uid"]).get()
        if quiz_id in user_quizzes:
            return JSONResponse(
                content=jsonable_encoder(user_quizzes[quiz_id])
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot find quiz with id {quiz_id}"
            )
    except FirebaseError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Successful Response"
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
async def delete_user_quizzes(body: DeleteUserQuizzes,user=Depends(get_user_token)):
    """
    Delete user quizzes.
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
            ref = db.reference("Quizzes")
            user_quizzes = ref.order_by_child("uid").equal_to(user["uid"]).get()
            for quiz_id in body.quizzes_ids:
                if quiz_id in user_quizzes:
                    ref.child(quiz_id).delete()
            return Response(
                status_code=status.HTTP_204_NO_CONTENT
            )
    except FirebaseError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.delete(
    "/{quiz_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Successful Response"
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
async def delete_user_quiz(quiz_id: str, user=Depends(get_user_token)):
    """
    Delete user quiz.
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
        ref = db.reference("Quizzes")
        user_quizzes = ref.order_by_child("uid").equal_to(user["uid"]).get()
        if quiz_id in user_quizzes:
            ref.child(quiz_id).delete()
            return Response(
                status_code=status.HTTP_204_NO_CONTENT
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot find quiz with id {quiz_id}"
            )
    except FirebaseError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.patch(
    "/{quiz_id}",
    responses={
        status.HTTP_200_OK: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "category": "History",
                        "difficulty": "easy",
                        "questions": [
                            {
                            "correct_answer": "in London in 1912",
                            "incorrect_answers": [
                                "in Manchester in 1901",
                                "in Oxford in 1924",
                                "in Cambridge in 1935"
                            ],
                            "question": "Where and when was Alan Turing born?"
                            },
                            {
                            "correct_answer": "a Turing Machine",
                            "incorrect_answers": [
                                "the Bombe",
                                "Church's Computer",
                                "the Manchester Mach I"
                            ],
                            "question": "Turing, while solving the Decision Problem, proposed a hypothetical computing machine, which we now call ___"
                            }
                        ],
                        "tags": "1910's",
                        "title": "The father of the computer",
                        "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
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
async def patch_user_quiz(quiz_id: str, body: UpdateUserQuiz, user=Depends(get_user_token)):
    """
    Update user quiz.
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
        ref = db.reference("Quizzes")
        user_quizzes = ref.order_by_child("uid").equal_to(user["uid"]).get()
        if quiz_id in user_quizzes:
            user_quiz = UserQuiz(
                **{
                    **user_quizzes[quiz_id],
                    **{k: v for k, v in body.dict().items() if v is not None}
                }
            )
            ref.child(quiz_id).set(user_quiz.dict())
            return JSONResponse(
                content=jsonable_encoder(user_quiz)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot find quiz with id {quiz_id}"
            )
    except FirebaseError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
