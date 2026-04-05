from pathlib import Path

from core.ports import RecipeRepository
from domain.recipe_record import RecipeRecord
from logger import logger


class LocalJsonRecipeRepository(RecipeRepository):
    def __init__(self, target_dir: str = "db"):
        self.target_dir = Path(target_dir)

    def save(
        self,
        recipe_record: RecipeRecord,
        source_id: str | None = None,
    ) -> RecipeRecord | None:
        if not source_id:
            logger.error("source_id is required to save recipe JSON locally.")
            return None

        self.target_dir.mkdir(parents=True, exist_ok=True)
        recipe_path = self.target_dir / f"{source_id}.json"
        recipe_path.write_text(
            recipe_record.model_dump_json(indent=2), encoding="utf-8"
        )
        logger.info(f"Recipe saved to: {recipe_path}")
        return recipe_record
