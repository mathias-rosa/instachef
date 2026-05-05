import argparse
import asyncio

from dotenv import load_dotenv

from connectors.cli import CLIConnector
from connectors.telegram import TelegramConnector
from infrastructure.config import AppConfig
from infrastructure.container import build_process_reel_service, build_repository
from logger import logger

load_dotenv()


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run InstaChef in different modes.")
    parser.add_argument(
        "--mode",
        choices=["cli", "telegram"],
        default="cli",
        help="Choose the mode to run: 'cli' (default) or 'telegram'.",
    )
    args = parser.parse_args()

    config = AppConfig.from_env()
    repository = build_repository(config=config)
    service = build_process_reel_service(config=config, repository=repository)

    if args.mode == "cli":
        connector = CLIConnector(service=service)
    elif args.mode == "telegram":
        token = config.telegram_bot_token
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN must be set for telegram mode.")
            raise ValueError("TELEGRAM_BOT_TOKEN must be set")

        connector = TelegramConnector(
            reelsProcessingService=service,
            recipeRepository=repository,
            token=token,
            authorized_user_ids=set(config.telegram_authorized_user_ids),
        )
    else:
        logger.error(f"Unsupported mode: {args.mode}")
        raise ValueError(f"Unsupported mode: {args.mode}")

    await connector.run()


if __name__ == "__main__":
    asyncio.run(main())
