from typing import Annotated

from pydantic import BaseModel, Field, computed_field

from domain.recipe import Recipe
from domain.recipe_source import (
    PhotoRecipeSource,
    ReelRecipeSource,
    TextRecipeSource,
)


class RecipeRecord(BaseModel):
    recipe: Recipe
    source: Annotated[
        ReelRecipeSource | PhotoRecipeSource | TextRecipeSource,
        Field(discriminator="source_type"),
    ]

    @computed_field
    @property
    def id(self) -> str:
        return self.source.canonical_id()
