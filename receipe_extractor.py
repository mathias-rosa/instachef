from pathlib import Path
from pydantic_ai import Agent, BinaryContent
from models import Recipe
from logger import logger


class RecipeExtractor:
    MODEL = "gemini-3.1-flash-lite-preview"

    def __init__(self):
        self.agent = Agent(
            self.MODEL,
            output_type=Recipe,
            instructions=(
                "You are an expert culinary assistant. Analyze the recipe video "
                "(Instagram Reel) and the caption provided by the user. "
                "Extract information and generate a structured recipe that is "
                "simple and concise. If steps are missing from the description, "
                "use the video to infer them. Language: French. Units: metric."
            ),
        )

    def extract_recipe(self, video_path: str, caption: str) -> str | None:
        try:
            video_bytes = Path(video_path).read_bytes()
        except Exception as e:
            logger.error(f"Could not read video file: {e}")
            return None

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
            return None

        output = result.output
        if isinstance(output, Recipe):
            return output.model_dump_json()
        return output

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
