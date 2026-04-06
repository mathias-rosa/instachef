from pathlib import Path

from pydantic_ai import Agent, BinaryContent

from domain.exceptions import (
    RecipeGenerationError,
    UnexpectedExtractionOutputError,
    VideoReadError,
)
from domain.recipe import Recipe
from logger import logger


class AiRecipeExtractor:
    def __init__(self, model_name: str):
        self.agent = Agent(
            model_name,
            output_type=Recipe,
            instructions=SYSTEM_PROMPT,
        )

    def extract_recipe(self, video_path: str, caption: str) -> Recipe:
        try:
            video_bytes = Path(video_path).read_bytes()
        except Exception as e:
            raise VideoReadError(f"Could not read video file: {e}") from e

        logger.info("Generating recipe...")

        prompt = self._build_prompt(caption)
        video_content = BinaryContent(
            data=video_bytes,
            media_type=self._detect_media_type(video_path),
        )

        try:
            result = self.agent.run_sync([prompt, video_content])
        except Exception as e:
            raise RecipeGenerationError(f"Error generating recipe: {e}") from e

        output = result.output
        if isinstance(output, Recipe):
            return output

        raise UnexpectedExtractionOutputError(
            "Recipe extraction returned unexpected output type."
        )

    @staticmethod
    def _build_prompt(caption: str) -> str:
        return f"""Original caption:
{caption}
"""

    @staticmethod
    def _detect_media_type(video_path: str) -> str:
        suffix = Path(video_path).suffix.lower()
        if suffix == ".mp4":
            return "video/mp4"
        if suffix == ".mov":
            return "video/quicktime"
        return "application/octet-stream"


SYSTEM_PROMPT = """You are an expert culinary assistant specialized in analyzing cooking videos.

Analyze the Instagram Reel video and the caption provided. Extract all available 
information and generate a structured recipe.

Guidelines:
- Language: French exclusively.
- Units: metric system only.
- If information is missing or cannot be inferred, use null — never invent data.
- Split complex components (marinades, sauces, doughs, toppings) into sub_recipes.
  Each sub_recipe must have a unique snake_case id (e.g. "marinade", "sauce_ail").
- In main instructions, reference sub_recipes using {{sub_recipe:id}} syntax.
  Example: "Faites mariner le poulet dans {{sub_recipe:marinade}} pendant 1 heure."
- For ingredients: separate name, quantity (numeric), unit, count (whole units), 
  and preparation note strictly.
- For appliances: only list electric appliances actually required (oven, airfryer...).
- For utensils: only list non-basic equipment (wok, mandoline, piping bag...).
  Omit knives, bowls, cutting boards.
- For tags: short lowercase keywords about style or dietary info.
- For tips: practical advice from the creator seen in the video or caption.
- Difficulty reflects technique required, not number of steps.
"""
