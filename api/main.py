import argparse
import asyncio

from dotenv import load_dotenv

from connectors.api import ApiConnector
from connectors.cli import CLIConnector
from connectors.telegram import TelegramConnector
from infrastructure.config import AppConfig
from infrastructure.container import build_process_reel_service, build_repository
from logger import logger

load_dotenv()


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run InstaChef connectors in parallel.",
    )
    parser.add_argument(
        "--mode",
        choices=["cli", "telegram", "api"],
        action="append",
        default=None,
        help=(
            "Choose one or more modes to run. Repeat the flag to start multiple connectors."
        ),
    )
    args = parser.parse_args()

    config = AppConfig.from_env()
    repository = build_repository(config=config)
    service = build_process_reel_service(config=config, repository=repository)

    connectors = []
    selected_modes = set(args.mode or ["cli", "telegram", "api"])

    if "cli" in selected_modes:
        connectors.append(CLIConnector(service=service))

    if "telegram" in selected_modes:
        token = config.telegram_bot_token
        if not token:
            message = "TELEGRAM_BOT_TOKEN must be set for telegram mode."
            if selected_modes == {"telegram"}:
                logger.error(message)
                raise ValueError("TELEGRAM_BOT_TOKEN must be set")
            logger.warning("%s Skipping Telegram connector.", message)
        else:
            connectors.append(
                TelegramConnector(
                    reelsProcessingService=service,
                    recipeRepository=repository,
                    token=token,
                    authorized_user_ids=set(config.telegram_authorized_user_ids),
                )
            )

    if "api" in selected_modes:
        connectors.append(
            ApiConnector(
                service=service,
                repository=repository,
                host=config.api_host,
                port=config.api_port,
            )
        )

    if not connectors:
        logger.error("No connectors configured for the selected mode.")
        raise ValueError("No connectors configured for the selected mode")

    await asyncio.gather(*(connector.run() for connector in connectors))


if __name__ == "__main__":
    asyncio.run(main())
