import os

from core.ports import RecipeExtractor, RecipeRepository, ReelDownloader
from domain.exceptions import NotARecipeError
from domain.recipe_record import RecipeRecord
from domain.recipe_source import ReelRecipeSource
from logger import logger


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

    def execute(self, reel_url: str) -> RecipeRecord:
        downloaded = self.downloader.download_reel(reel_url)

        try:
            source = ReelRecipeSource(
                reel_url=reel_url,
                shortcode=downloaded.shortcode,
                caption=downloaded.caption,
                author=downloaded.author,
            )

            existing_record = self.repository.find_by_id(source.canonical_id())
            if existing_record:
                logger.info(
                    f"Source already processed, reusing stored record: {existing_record.id}"
                )
                return existing_record

            recipe = self.extractor.extract_recipe(
                downloaded.video_path, downloaded.caption
            )

            if not recipe.is_recipe:
                logger.info("The extracted content is not a valid recipe.")
                raise NotARecipeError("The extracted content is not a valid recipe.")

            recipe_result = RecipeRecord(
                recipe=recipe,
                source=source,
            )
            saved = self.repository.save(recipe_result)
            return saved
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
