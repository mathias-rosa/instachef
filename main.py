from dotenv import load_dotenv
from recipe_processor import RecipeProcessor


load_dotenv()


def main():
    processor = RecipeProcessor()

    reel_url = input("Enter Instagram Reel URL: ")

    recipe = processor.process_reel(reel_url)

    if recipe:
        print("\n=== EXTRACTED RECIPE ===")
        print(f"Title: {recipe.title}")
        print("\nIngredients:")
        for ingredient in recipe.ingredients:
            print(f"  - {ingredient}")
        print("\nInstructions:")
        for i, instruction in enumerate(recipe.instructions, 1):
            print(f"  {i}. {instruction}")
        print("=" * 25)
    else:
        print("Failed to extract recipe.")


if __name__ == "__main__":
    main()
