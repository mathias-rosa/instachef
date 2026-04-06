from supabase import Client, create_client

from core.ports import RecipeRepository
from domain.exceptions import RepositoryReadError, RepositoryWriteError
from domain.recipe_record import RecipeRecord
from logger import logger


class SupabaseRecipeRepository(RecipeRepository):
    TABLE_NAME = "recipes"

    def __init__(self, url: str, key: str) -> None:
        self.client: Client = create_client(url, key)

    def save(
        self,
        recipe_record: RecipeRecord,
    ) -> RecipeRecord:
        try:
            payload = recipe_record.model_dump(mode="json")
            response = (
                self.client.table(self.TABLE_NAME)
                .upsert(
                    payload,
                    on_conflict="id",
                )
                .execute()
            )

            rows = getattr(response, "data", None)
            if not rows:
                logger.error("Supabase upsert returned no rows.")
                raise RepositoryWriteError("Supabase upsert returned no rows.")

            first_row = rows[0]
            return RecipeRecord.model_validate(first_row)
        except Exception as exc:
            if isinstance(exc, RepositoryWriteError):
                raise
            logger.error(f"Error saving recipe to Supabase: {exc}")
            raise RepositoryWriteError(
                f"Error saving recipe to Supabase: {exc}"
            ) from exc

    def find_by_id(self, record_id: str) -> RecipeRecord | None:
        try:
            response = (
                self.client.table(self.TABLE_NAME)
                .select("*")
                .eq("id", record_id)
                .limit(1)
                .execute()
            )
            rows = getattr(response, "data", None)
            if not rows:
                return None

            return RecipeRecord.model_validate(rows[0])
        except Exception as exc:
            logger.error(f"Error finding recipe by id in Supabase: {exc}")
            raise RepositoryReadError(
                f"Error finding recipe by id in Supabase: {exc}"
            ) from exc
