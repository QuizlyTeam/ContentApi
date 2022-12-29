from typing import Union

from pydantic import BaseModel, Field


class CreateUserAccount(BaseModel):
    nickname: str = Field(
        min_length=3,
        max_length=30,
        regex="^[A-Za-z0-9]+([A-Za-z0-9]*|[._-]?[A-Za-z0-9]+)*$",
    )


class UserAccount(BaseModel):
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
