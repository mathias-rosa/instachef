from core.process_reel import ProcessReelService
from domain.recipe import Recipe

PROMPT_REEL_URL = "Enter Instagram Reel URL: "


def print_recipe(recipe: Recipe) -> None:
    print("\n=== EXTRACTED RECIPE ===")
    print(f"Title: {recipe.title}")
    print("\nIngredients:")
    for ingredient in recipe.ingredients:
        print(f"  - {ingredient}")
    print("\nInstructions:")
    for i, instruction in enumerate(recipe.instructions, 1):
        if hasattr(instruction, "title") and hasattr(instruction, "description"):
            prefix = f"{instruction.title}: " if instruction.title else ""
            print(f"  {i}. {prefix}{instruction.description}")
        else:
            print(f"  {i}. {instruction}")
    print("=" * 25)


def run_cli(service: ProcessReelService) -> Recipe | None:
    reel_url = input(PROMPT_REEL_URL)
    return service.execute(reel_url)
