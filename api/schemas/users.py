from typing import Union

from pydantic import BaseModel, Field


class CreateUserAccount(BaseModel):
    """
    This is used to create a new user account.
    :param nickname: - the nickname for the user account.
    """

    nickname: str = Field(
        min_length=3,
        max_length=30,
        regex="^[A-Za-z0-9]+([A-Za-z0-9]*|[._-]?[A-Za-z0-9]+)*$",
    )


class UserAccount(BaseModel):
    """
    The user account model. This is the model that is used to store the user account data.
    :param uid: - the user id, this is the unique identifier for the user account.
    :param nickname: - the nickname of the user account.
    :param name: - the name of the user account.
    :param picture: - the picture of the user account.
    :param win: - the number of wins of the user account.
    :param lose: - the number of losses of the user account.
    :param favourite_category: - the favourite category of the user account.
    :param max_points: - the maximum points of the user account.
    """

    uid: str = Field(min_length=28, max_length=28)
    nickname: str = Field(
        min_length=3,
        max_length=30,
        regex="^[A-Za-z0-9]+([A-Za-z0-9]*|[._-]?[A-Za-z0-9]+)*$",
    )
    name: str
    picture: str
    win: int
    lose: int
    favourite_category: str
    max_points: Union[int, float]
