import argparse
import asyncio
import os

from dotenv import load_dotenv

from connectors.cli import CLIConnector
from connectors.telegram import TelegramConnector
from infrastructure.container import build_process_reel_service

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

    service = build_process_reel_service()

    if args.mode == "cli":
        connector = CLIConnector(service=service)
    elif args.mode == "telegram":
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN must be set")

        authorized_user_ids = os.getenv("TELEGRAM_AUTHORIZED_USER_IDS", "")
        user_ids = (
            [int(uid) for uid in authorized_user_ids.split(",") if uid.strip()]
            if authorized_user_ids
            else []
        )
        connector = TelegramConnector(
            service=service, token=token, authorized_user_ids=user_ids
        )
    else:
        raise ValueError(f"Unsupported mode: {args.mode}")

    await connector.run()


if __name__ == "__main__":
    asyncio.run(main())
