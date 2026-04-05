# InstaCHEF

InstaCHEF turns an Instagram reel into a structured recipe. The project follows a simple pipeline: download the reel, extract structured data with an LLM, then persist a normalized domain object as JSON.

## Project Overview

The code is organized into three layers:

- `domain/` contains the Pydantic business models.
- `core/` contains the ports and orchestration service.
- `providers/` contains the concrete implementations: LLM extraction, JSON storage, reel downloading.
- `connectors/` contains user-facing entry points, currently mostly the CLI.

### Structure

```text
main.py                      CLI entry point
connectors/
  cli.py                     Console output
  rest.py                    Minimal HTTP adapter
core/
  ports.py                   Business protocols
  process_reel.py            Workflow orchestration
domain/
  recipe.py                  Recipe business model
  recipe_source.py           Recipe provenance
  reel.py                    Downloaded reel data
providers/
  ai_recipe_extractor.py     Pydantic AI + Gemini extraction
  local_json_recipe_repository.py  Local JSON persistence
  reels_downloader.py        Reel download logic
db/                          Saved recipes
downloaded_reels/            Temporary downloaded files
```

## Data Model

The core of the project is made of two objects:

- `Recipe` represents the normalized recipe: title, description, dish type, difficulty, time, servings, ingredients, sub-recipes, steps, tags, and tips.
- `RecipeResult` wraps the recipe together with its source.

For now, the only implemented source is `ReelRecipeSource`. It includes:

- `source_type`
- `reel_url`
- `shortcode`
- `author`
- `caption`
- `preview_url`

This separation makes it easy to add future sources such as free text or images without changing the recipe model itself.

## How It Works

The current flow is:

1. The user provides an Instagram reel URL.
2. The reel is downloaded locally.
3. The LLM extracts a structured recipe.
4. The service builds a `RecipeResult` with the Instagram source.
5. The result is saved as JSON in `db/`.
6. The temporary video file is removed.

## Installation

Requirements:

- Python 3.13+
- `uv`

Install dependencies:

```bash
uv sync
```

Then configure the Gemini key in your environment:

```bash
export GEMINI_API_KEY="your-key"
```

Or in a `.env` file:

```env
GEMINI_API_KEY=your-gemini-key
```

## Usage

Run the CLI:

```bash
uv run main.py
```

The program asks for an Instagram reel URL, processes the video, and prints the extracted recipe in the terminal. The JSON is also saved to `db/<shortcode>.json`.

## Output Example

The saved JSON looks like this:

```json
{
  "recipe": {
    "title": "Bols de Riz au Poulet Shawarma (One-Pan)",
    "description": "...",
    "cuisine_type": "moyen-orientale",
    "dish_type": "plat principal",
    "difficulty": "moyen",
    "ingredients": [],
    "instructions": []
  },
  "source": {
    "source_type": "reel",
    "reel_url": "https://www.instagram.com/reel/...",
    "shortcode": "...",
    "author": "..."
  }
}
```

## Local Preview

A static preview page lives in `recipe-preview.html`. It can read JSON files from `db/` and render the recipe in a more visual layout.

To test it locally, serve the workspace root and open the page in your browser:

```bash
python3 -m http.server
```

Then open:

```text
http://localhost:8000/recipe-preview.html?recipe=DLIBdQjt7oM
```

## LLM Configuration

The extraction provider uses Pydantic AI with Gemini. The system prompt currently enforces:

- French output only
- metric units only
- sub-recipes for self-contained components
- a stable, structured recipe format

## Planned Evolution

The source model is designed to grow over time. Future additions may include:

- text input sources
- image input sources
- extra application-specific metadata if needed

The goal is to keep `Recipe` as a pure business object and store provenance separately in `RecipeResult`.

## Notes

- Existing JSON files in `db/` may need migration to the wrapped format.
- The `downloaded_reels/` directory contains temporary artifacts that are cleaned up after processing.

## Setup Database

To manually create the `recipes` table in Supabase, execute the following SQL command in the Supabase SQL Editor:

```sql
CREATE TABLE IF NOT EXISTS recipes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  recipe jsonb NOT NULL,
  source jsonb NOT NULL,
  created_at timestamp with time zone DEFAULT NOW(),
  updated_at timestamp with time zone DEFAULT NOW()
);

ALTER TABLE recipes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all access" ON recipes
  FOR ALL USING (TRUE);

CREATE INDEX IF NOT EXISTS idx_recipes_created_at ON recipes(created_at);
```

