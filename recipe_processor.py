import json
import os
from pathlib import Path
from instagram_client import InstagramClient
from receipe_extractor import RecipeExtractor
from models import Recipe
from logger import logger


class RecipeProcessor:
    def __init__(self, target_dir: str = "downloaded_reels"):
        self.instagram = InstagramClient(target_dir=target_dir)
        self.gemini = RecipeExtractor()
        self.target_dir = target_dir

    def process_reel(self, reel_url: str) -> Recipe | None:
        downloaded = self.instagram.download_reel(reel_url)
        if not downloaded:
            return None

        video_path, caption, shortcode = downloaded

        recipe_json = self.gemini.extract_recipe(video_path, caption)
        if not recipe_json:
            self._cleanup_video(video_path)
            return None

        recipe = self._parse_recipe_json(recipe_json)

        if recipe:
            self._save_recipe(recipe, shortcode)

        self._cleanup_video(video_path)
        return recipe

    @staticmethod
    def _parse_recipe_json(recipe_json: str) -> Recipe | None:
        try:
            data = json.loads(recipe_json)
            return Recipe(**data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing recipe: {e}")
            return None

    def _save_recipe(self, recipe: Recipe, shortcode: str) -> None:
        recipe_path = Path(self.target_dir) / f"{shortcode}_recipe.json"
        recipe_path.write_text(recipe.model_dump_json(indent=2), encoding="utf-8")
        logger.info(f"Recipe saved to: {recipe_path}")

    @staticmethod
    def _cleanup_video(video_path: str) -> None:
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                logger.debug(f"Cleaned up video: {video_path}")
        except Exception as e:
            logger.error(f"Error cleaning up video: {e}")
