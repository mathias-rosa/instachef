from core.process_reel import ProcessReelService
from infrastructure.config import AppConfig
from logger import logger
from providers.ai_recipe_extractor import AiRecipeExtractor
from providers.local_json_recipe_repository import LocalJsonRecipeRepository
from providers.mongodb_recipe_repository import MongoDBRecipeRepository
from providers.reels_downloader import ReelDownloader
from providers.supabase_recipe_repository import SupabaseRecipeRepository


def build_process_reel_service(
    config: AppConfig,
    target_dir: str = "downloaded_reels",
) -> ProcessReelService:
    downloader = ReelDownloader(target_dir=target_dir)
    extractor = AiRecipeExtractor(model_name=config.ai_model)
    repository = _build_repository(config)
    return ProcessReelService(
        downloader=downloader,
        extractor=extractor,
        repository=repository,
    )


def _build_repository(config: AppConfig):
    if config.repository_backend == "local_json":
        return LocalJsonRecipeRepository(target_dir=config.local_json_target_dir)

    if config.repository_backend == "supabase":
        if not config.supabase_url or not config.supabase_key:
            logger.error(
                "SUPABASE_URL and SUPABASE_KEY must be set for Supabase backend."
            )
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        return SupabaseRecipeRepository(
            url=config.supabase_url,
            key=config.supabase_key,
        )

    if config.repository_backend == "mongodb":
        if not config.mongodb_uri:
            logger.error("MONGODB_URI must be set for MongoDB backend.")
            raise ValueError("MONGODB_URI must be set")
        return MongoDBRecipeRepository(
            uri=config.mongodb_uri,
            database_name=config.mongodb_database,
            collection_name=config.mongodb_collection,
        )

    logger.error(f"Unsupported repository backend: {config.repository_backend}")
    raise ValueError(f"Unsupported repository backend: {config.repository_backend}")
