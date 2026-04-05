# 🍳 InstaCHEF

Transform Instagram Reels into structured recipes using Google Gemini AI.

## Architecture

Clean modular architecture for easy evolution and reusability:

```
main.py                 ← CLI entry point
    ↓
recipe_processor.py     ← Main orchestrator
    ├→ instagram_client.py  ← Instagram Reel management
    ├→ gemini_client.py     ← Google Gemini API integration
    └→ models.py            ← Data models (Pydantic)
```

### Modules

- **`models.py`** : Defines `Recipe` data structure (title, ingredients, instructions).
- **`instagram_client.py`** : Encapsulates Reel download logic via `instaloader`.
- **`gemini_client.py`** : Handles Gemini 2.5 Flash API communication and recipe extraction.
- **`recipe_processor.py`** : Orchestrates workflow (download → extract → save → cleanup).
- **`main.py`** : Simple CLI interface delegating to `RecipeProcessor`.

## Setup

### Requirements
- Python 3.13+
- `uv` (package manager)

### Installation

```bash
cd instachef

uv sync

export GEMINI_API_KEY="your-api-key-from-aistudio.google.com"
```

Or edit `.env` directly:

```
GEMINI_API_KEY=your-google-ai-studio-api-key-here
```

## Usage

```bash
uv run main.py
```

Enter an Instagram Reel URL when prompted. The app will:
1. Download the video and caption
2. Extract recipe using Gemini 2.5 Flash
3. Save as JSON
4. Delete the local video file

## Output Example

```json
{
  "title": "Classic Pasta Carbonara",
  "ingredients": [
    "400g tagliatelle pasta",
    "200g bacon",
    "3 eggs",
    "100g parmesan",
    "Black pepper",
    "Salt"
  ],
  "instructions": [
    "Boil salted water and cook pasta.",
    "Fry bacon until crispy.",
    "Mix eggs with cheese and pepper.",
    "Combine hot pasta with hot bacon and egg mixture."
  ]
}
```

## Future Extensibility

### Telegram Bot
```python
from telegram.ext import Application
from recipe_processor import RecipeProcessor

processor = RecipeProcessor()

async def handle_reel(update, context):
    recipe = processor.process_reel(update.message.text)
    # Send to user
```

### REST API (FastAPI)
```python
from fastapi import FastAPI
from recipe_processor import RecipeProcessor

app = FastAPI()
processor = RecipeProcessor()

@app.post("/extract")
async def extract(url: str):
    return processor.process_reel(url)
```

### Docker
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
CMD ["uv", "run", "main.py"]
```

## Costs

- **Gemini API** : Free tier up to 50 requests/day
- **Instaloader** : No cost
- **Infrastructure** : Minimal (Lambda-friendly)
