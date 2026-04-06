from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel, Field


class RecipeSource(BaseModel, ABC):
    @abstractmethod
    def canonical_id(self) -> str: ...


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

    def canonical_id(self) -> str:
        return f"reel:{self.shortcode}"


class PhotoRecipeSource(RecipeSource):
    source_type: Literal["photo"] = "photo"
    photo_id: str = Field(
        description="Stable photo fingerprint or external identifier."
    )
    original_url: str | None = Field(
        None,
        description="Original photo URL when available.",
    )
    caption: str | None = Field(
        None,
        description="Original photo caption.",
    )

    def canonical_id(self) -> str:
        return f"photo:{self.photo_id}"


class TextRecipeSource(RecipeSource):
    source_type: Literal["text"] = "text"
    text_id: str = Field(description="Stable text fingerprint or external identifier.")
    author: str | None = Field(
        None,
        description="Author or sender of the text, when available.",
    )
    caption: str | None = Field(
        None,
        description="Original message text or caption.",
    )

    def canonical_id(self) -> str:
        return f"text:{self.text_id}"
