from core.process_reel import ProcessReelService
from domain.recipe import Recipe


class TelegramConnector:
    def __init__(self, service: ProcessReelService):
        self.service = service

    def handle_reel_url(self, reel_url: str) -> Recipe | None:
        return self.service.execute(reel_url)
