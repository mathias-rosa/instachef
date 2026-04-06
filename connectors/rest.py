from core.process_reel import ProcessReelService
from domain.recipe_record import RecipeRecord


class RestConnector:
    def __init__(self, service: ProcessReelService):
        self.service = service

    def handle_reel_url(self, reel_url: str) -> RecipeRecord:
        return self.service.execute(reel_url)
