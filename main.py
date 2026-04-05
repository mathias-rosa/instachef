from dotenv import load_dotenv

from logger import logger
from connectors.cli import print_recipe, run_cli
from infrastructure.container import build_process_reel_service


load_dotenv()


def main() -> None:
    service = build_process_reel_service()
    recipe = run_cli(service=service)

    if recipe:
        print_recipe(recipe)
    else:
        logger.warning("Failed to extract recipe.")


if __name__ == "__main__":
    main()
