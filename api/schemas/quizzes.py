from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Extra, Field, root_validator


class CategoriesModel(BaseModel):
    """
    A model that contains a list of categories.
    :param categories: - the list of categories
    """

    categories: List[str]


class TagsModel(BaseModel):
    """
    A model that contains a list of tags.
    :param tags: - the list of tags
    """

    tags: List[str]


class GameJoinModel(BaseModel):
    """
    The GameJoinModel class is used to validate the data that is sent to the server.
    :param nickname: - the nickname of the user
    :param uid: - the uid of the user
    :param quiz_id: - the quiz id of the game
    :param categories: - the categories of the game
    :param difficulty: - the difficulty of the game
    :param limit: - the limit of the game
    :param tags: - the tags of the game
    :param max_players: - the max players of the game
    """

    nickname: str = Field(
        min_length=3,
        max_length=30,
        regex="^[A-Za-z0-9]+([A-Za-z0-9]*|[._-]?[A-Za-z0-9]+)*$",
    )
    uid: Optional[str] = Field(min_length=28, max_length=28)
    quiz_id: Optional[str] = Field(min_length=20, max_length=20)
    categories: Optional[Union[str, List[str]]] = Field(
        min_length=5, max_length=30
    )
    difficulty: Optional[Literal["easy", "medium", "hard"]]
    limit: Optional[int] = 5
    tags: Optional[Union[str, List[str]]]
    max_players: Optional[int] = 1

    @root_validator()
    def check_a_or_b(cls, values):
        if (values.get("uid") is None or values.get("quiz_id") is None) and (
            values.get("categories") is None
        ):
            raise ValueError("either a or b is required")
        return values

    class Config:
        extra = Extra.forbid


class GameCodeJoinModel(BaseModel):
    """
    The GameCodeJoinModel class is used to validate the data that is sent to the server.
    :param nickname: - the nickname of the user
    :param room: - websocket's room
    :param uid: - the uid of the user
    """

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
    """
    The GameAnswerModel class for the game answer model.
    """

    answer: str
    time: Union[float, int]

    class Config:
        extra = Extra.forbid


class Question(BaseModel):
    """
    The Question class defines the question structure.
    """

    question: str
    correct_answer: str
    incorrect_answers: List[str]

    class Config:
        extra = Extra.forbid


class UserQuiz(BaseModel):
    """
    The UserQuiz class is used to create a model that can be used to create a quiz.
    :param uid: - the quiz id
    :param title: - the quiz title
    :param category: - the quiz category
    :param difficulty: - the quiz difficulty
    :param tags: - the quiz tags
    :param questions: - the questions in the quiz
    """

    uid: str = Field(min_length=28, max_length=28)
    title: str = Field(min_length=1, max_length=200)
    category: Union[str, List[str]] = Field(min_length=5, max_length=30)
    difficulty: Literal["easy", "medium", "hard"]
    tags: Optional[Union[str, List[str]]]
    questions: List[Question]


class UserQuizzes(BaseModel):
    """
    The UserQuizzes class is used to store the quiz_id.
    :param quiz_id: - the quiz_id of the quiz.
    """

    quiz_id: UserQuiz


class DeleteUserQuizzes(BaseModel):
    """
    The DeleteUserQuizzes class is used to store the quizzes_ids to delete.
    @param quizzes_ids - the quizzes ids to delete
    """

    quizzes_ids: List[str]

    class Config:
        extra = Extra.forbid


class CreateUserQuiz(BaseModel):
    """
    This will be used to create a quiz for a user.
    :param title: - the title of the quiz.
    :param category: - the category of the quiz.
    :param difficulty: - the difficulty of the quiz.
    :param tags: - the tags of the quiz.
    :param questions: - the questions of the quiz.
    """

    title: str = Field(min_length=1, max_length=200)
    category: Union[str, List[str]] = Field(min_length=5, max_length=30)
    difficulty: Literal["easy", "medium", "hard"]
    tags: Optional[Union[str, List[str]]]
    questions: List[Question]

    class Config:
        extra = Extra.forbid


class UpdateUserQuiz(BaseModel):
    """
    The UpdateUserQuiz class is used to update the user quiz.
    :param title: - the title of the quiz.
    :param category: - the category of the quiz.
    :param difficulty: - the difficulty of the quiz.
    :param tags: - the tags of the quiz.
    :param questions: - the questions of the quiz.
    """

    title: Optional[str] = Field(min_length=1, max_length=200)
    category: Optional[Union[str, List[str]]] = Field(
        min_length=5, max_length=30
    )
    difficulty: Optional[Literal["easy", "medium", "hard"]]
    tags: Optional[Union[str, List[str]]]
    questions: Optional[List[Question]]

    @root_validator()
    def check_all(cls, values):
        if all(v is None for v in values.values()):
            raise ValueError("either a or b is required")
        return values

    class Config:
        extra = Extra.forbid
