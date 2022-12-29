from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, Extra, root_validator


class CategoriesModel(BaseModel):
    categories: List[str]


class TagsModel(BaseModel):
    tags: List[str]


class GameJoinModel(BaseModel):
    nickname: str = Field(
        min_length=3,
        max_length=30,
        regex="^[A-Za-z0-9]+([A-Za-z0-9]*|[._-]?[A-Za-z0-9]+)*$",
    )
    uid: Optional[str] = Field(min_length=28, max_length=28)
    quiz_id: Optional[str] = Field(min_length=20, max_length=20)
    categories: Optional[Union[str, List[str]]] = Field(min_length=5, max_length=30)
    difficulty: Optional[Literal["easy", "medium", "hard"]]
    limit: Optional[int] = 5
    tags: Optional[Union[str, List[str]]]
    max_players: Optional[int] = 1

    @root_validator()
    def check_a_or_b(cls, values):
        if (values.get('uid') is None or values.get('quiz_id') is None) and (values.get("categories") is None):
            raise ValueError('either a or b is required')
        return values

    class Config:
        extra = Extra.forbid


class GameCodeJoinModel(BaseModel):
    room: str
    nickname: str = Field(
        min_length=3,
        max_length=30,
        regex="^[A-Za-z0-9]+([A-Za-z0-9]*|[._-]?[A-Za-z0-9]+)*$",
    )
    uid: Optional[str] = Field(min_length=28, max_length=28)

    class Config:
        extra = Extra.forbid


class GameAnswerModel(BaseModel):
    answer: str
    time: Union[float, int]

    class Config:
        extra = Extra.forbid

class Question(BaseModel):
    question: str
    correct_answer: str
    incorrect_answers: List[str]

    class Config:
        extra = Extra.forbid

class UserQuiz(BaseModel):
    uid: str = Field(min_length=28, max_length=28)
    title: str = Field(min_length=1, max_length=200)
    category: Union[str, List[str]] = Field(min_length=5, max_length=30)
    difficulty: Literal["easy", "medium", "hard"]
    tags: Optional[Union[str, List[str]]]
    questions: List[Question]

class UserQuizzes(BaseModel):
    quiz_id: UserQuiz

class DeleteUserQuizzes(BaseModel):
    quizzes_ids: List[str]

    class Config:
        extra = Extra.forbid

class CreateUserQuiz(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    category: Union[str, List[str]] = Field(min_length=5, max_length=30)
    difficulty: Literal["easy", "medium", "hard"]
    tags: Optional[Union[str, List[str]]]
    questions: List[Question]

    class Config:
        extra = Extra.forbid

class UpdateUserQuiz(BaseModel):
    title: Optional[str] = Field(min_length=1, max_length=200)
    category: Optional[Union[str, List[str]]] = Field(min_length=5, max_length=30)
    difficulty: Optional[Literal["easy", "medium", "hard"]]
    tags: Optional[Union[str, List[str]]]
    questions: Optional[List[Question]]

    @root_validator()
    def check_all(cls, values):
        if all(v is None for v in values.values()):
            raise ValueError('either a or b is required')
        return values

    class Config:
        extra = Extra.forbid
