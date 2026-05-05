from pathlib import Path

from core.ports import RecipeRepository
from domain.exceptions import RepositoryReadError, RepositoryWriteError
from domain.recipe_record import RecipeRecord
from logger import logger


class LocalJsonRecipeRepository(RecipeRepository):
    def __init__(self, target_dir: str = "db"):
        self.target_dir = Path(target_dir)

    def save(
        self,
        recipe_record: RecipeRecord,
    ) -> RecipeRecord:
        if not recipe_record.id:
            logger.error("recipe_record.id is required to save recipe JSON locally.")
            raise RepositoryWriteError(
                "recipe_record.id is required to save recipe JSON locally."
            )

        try:
            self.target_dir.mkdir(parents=True, exist_ok=True)
            recipe_path = self._recipe_path(recipe_record.id)
            recipe_path.write_text(
                recipe_record.model_dump_json(indent=2), encoding="utf-8"
            )
            return recipe_record
        except Exception as exc:
            logger.error(f"Error saving recipe to local JSON store: {exc}")
            raise RepositoryWriteError(
                f"Error saving recipe to local JSON store: {exc}"
            ) from exc

    def find_by_id(self, record_id: str) -> RecipeRecord | None:
        recipe_path = self._recipe_path(record_id)
        if not recipe_path.exists():
            return None

        try:
            return RecipeRecord.model_validate_json(
                recipe_path.read_text(encoding="utf-8")
            )
        except Exception as exc:
            logger.error(f"Error loading recipe from local JSON store: {exc}")
            raise RepositoryReadError(
                f"Error loading recipe from local JSON store: {exc}"
            ) from exc

    def list_ids(self) -> list[str]:
        if not self.target_dir.exists():
            return []

        return sorted(
            path.stem.replace("__", ":")
            for path in self.target_dir.glob("*.json")
            if path.is_file()
        )

    def get_recent_recipes(self, limit: int = 10) -> list[RecipeRecord]:
        ids = self.list_ids()
        recent_ids = ids[-limit:] if ids else []

        recipes = []
        for record_id in reversed(recent_ids):
            try:
                record = self.find_by_id(record_id)
                if record:
                    recipes.append(record)
            except Exception as exc:
                logger.warning(f"Failed to load recipe {record_id}: {exc}")

        return recipes

    def _recipe_path(self, record_id: str) -> Path:
        safe_record_id = record_id.replace(":", "__")
        return self.target_dir / f"{safe_record_id}.json"
