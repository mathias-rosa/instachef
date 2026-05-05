from pymongo import MongoClient
from pymongo.errors import PyMongoError

from core.ports import RecipeRepository
from domain.exceptions import RepositoryReadError, RepositoryWriteError
from domain.recipe_record import RecipeRecord
from logger import logger


class MongoDBRecipeRepository(RecipeRepository):
    def __init__(
        self,
        uri: str,
        database_name: str,
        collection_name: str = "recipes",
    ) -> None:
        self.client = MongoClient(uri)
        self.collection = self.client[database_name][collection_name]

    def save(
        self,
        recipe_record: RecipeRecord,
    ) -> RecipeRecord:
        try:
            document = recipe_record.model_dump(mode="json")
            self.collection.replace_one(
                {"id": recipe_record.id},
                document,
                upsert=True,
            )

            saved_document = self.collection.find_one(
                {"id": recipe_record.id},
                {"_id": False},
            )
            if not saved_document:
                logger.error("MongoDB upsert returned no document.")
                raise RepositoryWriteError("MongoDB upsert returned no document.")

            return RecipeRecord.model_validate(saved_document)
        except RepositoryWriteError:
            raise
        except PyMongoError as exc:
            logger.error(f"Error saving recipe to MongoDB: {exc}")
            raise RepositoryWriteError(
                f"Error saving recipe to MongoDB: {exc}"
            ) from exc
        except Exception as exc:
            logger.error(f"Error saving recipe to MongoDB: {exc}")
            raise RepositoryWriteError(
                f"Error saving recipe to MongoDB: {exc}"
            ) from exc

    def find_by_id(self, record_id: str) -> RecipeRecord | None:
        try:
            document = self.collection.find_one({"id": record_id}, {"_id": False})
            if not document:
                return None

            return RecipeRecord.model_validate(document)
        except PyMongoError as exc:
            logger.error(f"Error finding recipe by id in MongoDB: {exc}")
            raise RepositoryReadError(
                f"Error finding recipe by id in MongoDB: {exc}"
            ) from exc
        except Exception as exc:
            logger.error(f"Error finding recipe by id in MongoDB: {exc}")
            raise RepositoryReadError(
                f"Error finding recipe by id in MongoDB: {exc}"
            ) from exc

    def list_ids(self) -> list[str]:
        try:
            cursor = self.collection.find({}, {"id": 1, "_id": 0}).sort("id", 1)
            return [document["id"] for document in cursor if document.get("id")]
        except PyMongoError as exc:
            logger.error(f"Error listing recipe ids in MongoDB: {exc}")
            raise RepositoryReadError(
                f"Error listing recipe ids in MongoDB: {exc}"
            ) from exc
        except Exception as exc:
            logger.error(f"Error listing recipe ids in MongoDB: {exc}")
            raise RepositoryReadError(
                f"Error listing recipe ids in MongoDB: {exc}"
            ) from exc

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
