from typing import Literal
from abc import ABC

from pydantic import BaseModel, Field


class RecipeSource(BaseModel, ABC):
    source_type: Literal["reel"]


class ReelRecipeSource(RecipeSource):
    source_type: Literal["reel"] = "reel"
    reel_url: str = Field(description="Original Instagram Reel URL")
    shortcode: str = Field(description="Unique identifier for the reel.")
    author: str = Field(
        description="Coontent creator name",
    )
    caption: str | None = Field(
        None,
        description="Original reel caption",
    )
