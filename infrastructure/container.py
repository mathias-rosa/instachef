from core.process_reel import ProcessReelService
from providers.ai_recipe_extractor import AiRecipeExtractor
from providers.local_json_recipe_repository import LocalJsonRecipeRepository
from providers.reels_downloader import ReelDownloader


def build_process_reel_service(
    target_dir: str = "downloaded_reels",
) -> ProcessReelService:
    downloader = ReelDownloader(target_dir=target_dir)
    extractor = AiRecipeExtractor()
    repository = LocalJsonRecipeRepository(target_dir="db")
    return ProcessReelService(
        downloader=downloader,
        extractor=extractor,
        repository=repository,
    )
