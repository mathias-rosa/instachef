from typing import Any

from supabase import Client, create_client

from core.ports import RecipeRepository
from domain.recipe import Recipe
from domain.recipe_record import RecipeRecord
from logger import logger


class SupabaseRecipeRepository(RecipeRepository):
    TABLE_NAME = "recipes"

    def __init__(self, url: str, key: str) -> None:
        self.client: Client = create_client(url, key)

    def save(
        self,
        recipe_record: RecipeRecord,
        source_id: str | None = None,
    ) -> RecipeRecord | None:
        try:
            payload = recipe_record.model_dump(mode="json")
            response = self.client.table(self.TABLE_NAME).insert(payload).execute()

            rows = getattr(response, "data", None)
            if not rows:
                logger.error("Supabase insert returned no rows.")
                return None

            first_row = rows[0]
            return RecipeRecord.model_validate(first_row)
        except Exception as exc:
            logger.error(f"Error saving recipe to Supabase: {exc}")
            return None

    def find_by_id(self, id: str) -> Recipe | None:
        try:
            response = (
                self.client.table(self.TABLE_NAME)
                .select("*")
                .eq("id", id)
                .limit(1)
                .execute()
            )
            rows = getattr(response, "data", None)
            if not rows:
                return None

            recipe_payload = self._extract_recipe_payload(rows[0])
            return Recipe.model_validate(recipe_payload)
        except Exception as exc:
            logger.error(f"Error finding recipe by id in Supabase: {exc}")
            return None

    @staticmethod
    def _extract_recipe_payload(row: dict[str, Any]) -> dict[str, Any]:
        recipe_payload = row.get("recipe")
        if isinstance(recipe_payload, dict):
            return recipe_payload
        return row
