from domain.recipe import Recipe
from domain.recipe_record import RecipeRecord
from typing import Protocol


from domain.reel import DownloadedReel


class ReelDownloader(Protocol):
    def download_reel(self, reel_url: str) -> DownloadedReel | None: ...


class RecipeExtractor(Protocol):
    def extract_recipe(self, video_path: str, caption: str) -> Recipe | None: ...


class RecipeRepository(Protocol):
    def save(self, recipe_result: RecipeRecord, source_id: str) -> None: ...
