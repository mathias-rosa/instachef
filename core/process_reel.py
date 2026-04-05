import os

from logger import logger
from core.ports import RecipeExtractor, RecipeRepository, ReelDownloader
from domain.recipe import Recipe
from domain.recipe_record import RecipeRecord
from domain.recipe_source import ReelRecipeSource


class ProcessReelService:
    def __init__(
        self,
        downloader: ReelDownloader,
        extractor: RecipeExtractor,
        repository: RecipeRepository,
    ):
        self.downloader = downloader
        self.extractor = extractor
        self.repository = repository

    def execute(self, reel_url: str) -> Recipe | None:
        downloaded = self.downloader.download_reel(reel_url)
        if not downloaded:
            return None

        try:
            recipe = self.extractor.extract_recipe(
                downloaded.video_path, downloaded.caption
            )
            if not recipe:
                return None

            recipe_result = RecipeRecord(
                recipe=recipe,
                source=ReelRecipeSource(
                    reel_url=reel_url,
                    shortcode=downloaded.shortcode,
                    caption=downloaded.caption,
                    author=downloaded.author,
                ),
            )
            self.repository.save(recipe_result, downloaded.shortcode)
            return recipe
        finally:
            self._cleanup_video(downloaded.video_path)

    @staticmethod
    def _cleanup_video(video_path: str) -> None:
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                logger.debug(f"Cleaned up video: {video_path}")
        except Exception as e:
            logger.error(f"Error cleaning up video: {e}")
