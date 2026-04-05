from pydantic import BaseModel


class Recipe(BaseModel):
    title: str
    ingredients: list[str]
    instructions: list[str]
