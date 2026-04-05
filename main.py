from dotenv import load_dotenv
from models import Recipe
from recipe_processor import RecipeProcessor
from logger import logger


load_dotenv()
PROMPT_REEL_URL = "Enter Instagram Reel URL: "


def _print_recipe(recipe: Recipe) -> None:
    print("\n=== EXTRACTED RECIPE ===")
    print(f"Title: {recipe.title}")
    print("\nIngredients:")
    for ingredient in recipe.ingredients:
        print(f"  - {ingredient}")
    print("\nInstructions:")
    for i, instruction in enumerate(recipe.instructions, 1):
        print(f"  {i}. {instruction}")
    print("=" * 25)


def main():
    processor = RecipeProcessor()
    reel_url = input(PROMPT_REEL_URL)

    recipe = processor.process_reel(reel_url)

    if recipe:
        _print_recipe(recipe)
    else:
        logger.warning("Failed to extract recipe.")


if __name__ == "__main__":
    main()
