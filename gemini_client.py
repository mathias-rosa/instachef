import time
from google import genai
from google.genai import types
from models import Recipe


class GeminiClient:
    MODEL = "gemini-3.1-flash-lite-preview"
    # MODEL = "gemini-2.5-flash"

    def __init__(self):
        self.client = genai.Client()

    def extract_recipe(self, video_path: str, caption: str) -> str | None:
        print("Uploading video to Google AI Studio...")
        uploaded_file = self.client.files.upload(file=video_path)

        while uploaded_file.state == "PROCESSING":
            print("Processing video, waiting...", end="\r")
            time.sleep(2)
            uploaded_file = self.client.files.get(name=uploaded_file.name)  # ty:ignore[invalid-argument-type]

        if uploaded_file.state == "FAILED":
            print("\nVideo processing failed.")
            return None

        print("\nGenerating recipe...")

        prompt = self._build_prompt(caption)

        response = self.client.models.generate_content(
            model=self.MODEL,
            contents=[uploaded_file, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Recipe,
            ),
        )

        self.client.files.delete(name=uploaded_file.name)  # ty:ignore[invalid-argument-type]

        return response.text

    @staticmethod
    def _build_prompt(caption: str) -> str:
        return f"""You are an expert culinary assistant. Analyze the recipe video (Instagram Reel) and the caption provided by the user.
Extract information and generate a structured JSON recipe that is simple and concise.

Original caption:
{caption}

If steps are missing from the description, use the video to infer them.

Generation rules:
- Language: French
- Units: Use metric units (grams, liters, etc.)
"""
