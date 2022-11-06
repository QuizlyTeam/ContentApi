from typing import List

from pydantic import BaseModel


class CategoriesModel(BaseModel):
    categories: List[str]
