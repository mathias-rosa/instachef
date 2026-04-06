from typing import Protocol

from domain.recipe import Recipe
from domain.recipe_record import RecipeRecord
from domain.reel import DownloadedReel


class ReelDownloader(Protocol):
    def download_reel(self, reel_url: str) -> DownloadedReel: ...


class RecipeExtractor(Protocol):
    def extract_recipe(self, video_path: str, caption: str) -> Recipe: ...


class RecipeRepository(Protocol):
    def save(
        self,
        recipe_record: RecipeRecord,
    ) -> RecipeRecord: ...

    def find_by_id(self, record_id: str) -> RecipeRecord | None: ...
