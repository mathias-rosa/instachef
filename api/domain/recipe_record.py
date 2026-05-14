from typing import Annotated

from pydantic import BaseModel, Field, model_validator

from domain.recipe import Recipe
from domain.recipe_source import (
    PhotoRecipeSource,
    ReelRecipeSource,
    TextRecipeSource,
)
from logger import logger


class RecipeRecord(BaseModel):
    id: str = Field(
        description="Canonical, stable identifier for the stored record.",
    )
    recipe: Recipe
    source: Annotated[
        ReelRecipeSource | PhotoRecipeSource | TextRecipeSource,
        Field(discriminator="source_type"),
    ]

    @model_validator(mode="after")
    def _set_canonical_id(self) -> "RecipeRecord":
        canonical_id = self.source.canonical_id()
        if self.id is None:
            self.id = canonical_id
        elif self.id != canonical_id:
            logger.error(
                f"RecipeRecord.id {self.id} does not match source canonical id {canonical_id}."
            )
            raise ValueError("RecipeRecord.id must match the source canonical id.")
        return self
