from pathlib import Path

from logger import logger
from domain.recipe import Recipe


class LocalJsonRecipeRepository:
    def __init__(self, target_dir: str = "db"):
        self.target_dir = Path(target_dir)

    def save(self, recipe: Recipe, source_id: str) -> None:
        self.target_dir.mkdir(parents=True, exist_ok=True)
        recipe_path = self.target_dir / f"{source_id}.json"
        recipe_path.write_text(recipe.model_dump_json(indent=2), encoding="utf-8")
        logger.info(f"Recipe saved to: {recipe_path}")
