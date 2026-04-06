import asyncio
from typing import cast

from connectors import InstachefConnector
from core.process_reel import ProcessReelService
from domain.exceptions import InstachefError, NotARecipeError
from domain.recipe import Recipe
from logger import logger

PROMPT_REEL_URL = "Enter Instagram Reel URL: "


class CLIConnector(InstachefConnector):
    def __init__(self, service: ProcessReelService) -> None:
        self.service = service

    async def run(self) -> None:
        while True:
            reel_url = await asyncio.to_thread(input, PROMPT_REEL_URL)
            reel_url = reel_url.strip()

            if reel_url.lower() == "exit":
                print("Exiting the application. Goodbye!")
                break

            if not reel_url:
                print("Error: No URL provided.")
                continue

            print("Processing the reel... This may take a few seconds.")
            try:
                recipe = cast(
                    Recipe,
                    await asyncio.to_thread(self.service.execute, reel_url),
                )
                print("\n✅ Recipe processed and saved successfully!")
                print(f"Title: {recipe.title}")
                print(f"Description: {recipe.description}")
            except NotARecipeError:
                print("Error: The extracted content is not a valid recipe.")
            except InstachefError as exc:
                logger.error(f"CLI processing error: {exc}")
                print(f"Error: {exc}")
            except Exception as exc:
                logger.error(f"CLI processing error: {exc}")
                print("An unexpected error occurred while processing the reel.")
