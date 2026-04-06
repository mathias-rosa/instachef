# InstaCHEF

InstaCHEF turns Instagram reels into structured recipes using AI. Download a reel, extract recipe data with an LLM (Gemini or compatible), and save it to Supabase—via CLI or Telegram bot.

## Quick Start

### Install dependencies

```bash
uv sync
```

### Configure (create .env)

```bash
cp .env.example .env
```

### Run CLI

```bash
uv run main.py --mode cli
```

### Or run Telegram bot

```bash
uv run main.py --mode telegram
```

For full setup instructions, see [Installation](#installation).

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

- `Recipe` represents the normalized recipe: title, description, dish type, difficulty, timing, servings, ingredients, instructions, tags, tips, appliances, and utensils.
- `RecipeRecord` wraps the recipe together with its source and a stable canonical identifier.

For now, the implemented source is `ReelRecipeSource`. It includes:

- `source_type`
- `reel_url`
- `shortcode`
- `author`
- `caption`

The canonical identifier is derived from the source, for example `reel:<shortcode>`. This lets the app detect that a document was already processed before trying to extract it again.

This separation makes it easy to add future sources such as photos or plain text without changing the recipe model itself.

## How It Works

The current flow is:

1. The user provides an Instagram reel URL.
2. The reel is downloaded locally.
3. The service checks whether the canonical record already exists.
4. If not, the LLM extracts a structured recipe.
5. The service builds a `RecipeRecord` with the source and canonical id.
6. The result is saved to Supabase or local JSON storage.
7. The temporary video file is removed.

## Installation

### Requirements

- Python 3.13+
- `uv`
- A Supabase account (for data storage)
- A Gemini API key (or another LLM provider)

### Setup

1. **Install dependencies:**

   ```bash
   uv sync
   ```

2. **Configure environment variables** (create a `.env` file):

   ```env
   # Supabase
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key

   # AI 
   AI_MODEL=gemini-3.1-flash-lite-preview
   GOOGLE_API_KEY=your-gemini-key

   # Telegram bot
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   TELEGRAM_AUTHORIZED_USER_IDS=123456789,987654321
   ```

3. **Configure Supabase database** (using the provided SQL script or via the dashboard).

### Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase anon key |
| `AI_MODEL` | No | Model name (default: `gemini-3.1-flash-lite-preview`) |
| `GOOGLE_API_KEY` | No | Gemini API key (Pydantic AI reads it automatically) |
| `TELEGRAM_BOT_TOKEN` | yes for `--mode telegram` | Telegram bot token |
| `TELEGRAM_AUTHORIZED_USER_IDS` | No | Comma-separated list of allowed Telegram user IDs |

**Note:** For other AI providers (OpenAI, Anthropic), set `AI_MODEL` to the appropriate model name and ensure the corresponding env var is set (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.). See [Pydantic AI models](https://ai.pydantic.dev/models/overview/).

## Usage

### CLI Mode (default)

```bash
uv run main.py
```

1. Enter an Instagram reel URL when prompted
2. The app downloads and processes the reel
3. Recipe data is extracted and saved to Supabase
4. Result is displayed in the terminal
5. Downloaded video is cleaned up

Type `exit` to quit the loop.

### Data Model & Output

Recipes are stored as `RecipeRecord` rows in Supabase or as JSON documents locally.

`RecipeRecord` contains:

- `id`: canonical identifier such as `reel:<shortcode>`
- `recipe`: extracted dish data
- `source`: provenance data

The `recipes` table should use a text primary key for `id`:

```sql
CREATE TABLE IF NOT EXISTS recipes (
  id text PRIMARY KEY,
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

## LLM Configuration

The extraction provider uses Pydantic AI with Gemini by default. The system prompt enforces:

- French output only
- metric units only
- sub-recipes for self-contained components
- a stable, structured recipe format

To use another provider, set `AI_MODEL` and the corresponding API key:

- OpenAI: `AI_MODEL=gpt-4o` + `OPENAI_API_KEY`
- Anthropic: `AI_MODEL=claude-3-5-sonnet` + `ANTHROPIC_API_KEY`

See [Pydantic AI models](https://ai.pydantic.dev/models/overview/) for the full list.

## Notes

- Existing JSON files in `db/` may need migration to the wrapped format.
- The `downloaded_reels/` directory contains temporary artifacts that are cleaned up after processing.

## Troubleshooting

### `SUPABASE_URL and SUPABASE_KEY must be set`

- Check your `.env` file or system environment variables.
- Verify you have a Supabase project created.

### `TELEGRAM_BOT_TOKEN must be set` when using `--mode telegram`

- Set `TELEGRAM_BOT_TOKEN` in your `.env`.
- Create a bot via [@BotFather](https://t.me/BotFather) on Telegram.

### `Error generating recipe`

- Check that your API key is valid and has quota remaining.
- Try with a different reel.

### Reel download fails

- Some reels are region-restricted or private.
- Try a different URL.

