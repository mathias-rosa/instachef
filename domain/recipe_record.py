from pydantic import BaseModel

from domain.recipe import Recipe
from domain.recipe_source import ReelRecipeSource


class RecipeRecord(BaseModel):
    recipe: Recipe
    source: ReelRecipeSource
