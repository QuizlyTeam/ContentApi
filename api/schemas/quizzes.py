from typing import List

from pydantic import BaseModel


class CategoriesModel(BaseModel):
    categories: List[str]


class TagsModel(BaseModel):
    tags: List[str]
