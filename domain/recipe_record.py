from domain.recipe import Recipe
from pydantic import BaseModel

from domain.recipe_source import ReelRecipeSource


class RecipeRecord(BaseModel):
    recipe: Recipe
    source: ReelRecipeSource
