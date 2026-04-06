from core.process_reel import ProcessReelService
from infrastructure.config import AppConfig
from providers.ai_recipe_extractor import AiRecipeExtractor
from providers.reels_downloader import ReelDownloader
from providers.supabase_recipe_repository import SupabaseRecipeRepository


def build_process_reel_service(
    config: AppConfig,
    target_dir: str = "downloaded_reels",
) -> ProcessReelService:
    downloader = ReelDownloader(target_dir=target_dir)
    extractor = AiRecipeExtractor(model_name=config.ai_model)
    repository = SupabaseRecipeRepository(
        url=config.supabase_url, key=config.supabase_key
    )
    return ProcessReelService(
        downloader=downloader,
        extractor=extractor,
        repository=repository,
    )
