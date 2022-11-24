from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field


class CategoriesModel(BaseModel):
    categories: List[str]


class GameJoinModel(BaseModel):
    name: str
    categories: Union[str, List[str]] = Field(min_length=5, max_length=30)
    difficulty: Optional[Literal["easy", "medium", "hard"]]
    limit: Optional[int] = 5
    tags: Optional[Union[str, List[str]]]
    with_friends: Optional[bool] = False
    max_players: Optional[int] = 1

class GameAnswerModel(BaseModel):
    answer: str
    time: Union[float, int]
