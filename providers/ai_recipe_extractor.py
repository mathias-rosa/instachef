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
            logger.error(f"Could not read video file: {e}")
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
            logger.error(f"Error generating recipe: {e}")
            raise RecipeGenerationError(f"Error generating recipe: {e}") from e

        output = result.output
        if isinstance(output, Recipe):
            return output

        logger.error("Recipe extraction returned unexpected output type.")
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

Analyze the Instagram Reel video and caption and output one structured Recipe object.

Guidelines:
- Output language: French only.
- Units: metric only (g, kg, ml, cl, l, c.à.c., c.à.s.).
- Never invent data. If unknown, use null or an empty list depending on the field.
- If the content is not a recipe, set is_recipe=false and still return a valid object.
    Use minimal neutral placeholders for required fields.
- Ingredients: keep name clean, put numbers in quantity/count, and prep details in note.
- Instructions: concise, actionable, chronological steps.
- Keep instructions aligned with ingredients and timings.
- Appliances: only electric devices actually needed.
- Utensils: only notable tools; exclude basic knife/board/bowl.
- Tags: short lowercase keywords relevant for search and filtering.
- Tips: only practical tips clearly present in video/caption.
- Difficulty should reflect technique complexity, not just recipe length.
"""
