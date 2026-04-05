import os

from core.process_reel import ProcessReelService
from providers.ai_recipe_extractor import AiRecipeExtractor
from providers.reels_downloader import ReelDownloader
from providers.supabase_recipe_repository import SupabaseRecipeRepository


def build_process_reel_service(
    target_dir: str = "downloaded_reels",
) -> ProcessReelService:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

    downloader = ReelDownloader(target_dir=target_dir)
    extractor = AiRecipeExtractor()
    repository = SupabaseRecipeRepository(url=supabase_url, key=supabase_key)
    return ProcessReelService(
        downloader=downloader,
        extractor=extractor,
        repository=repository,
    )
