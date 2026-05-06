# InstaCHEF

InstaCHEF turns Instagram reels into structured recipes using AI. Download a reel, extract recipe data with an LLM (Gemini or compatible), and save it to Supabase, MongoDB, or local JSON—via CLI or Telegram bot.

## Quick Start

### Install dependencies

```bash
uv sync
```

### Configure (create .env)

```bash
cp .env.example .env
```

### Run all connectors (CLI + API + Telegram when configured)

```bash
uv run main.py
```

### Run CLI only

```bash
uv run main.py --mode cli
```

### Run Telegram bot only

```bash
uv run main.py --mode telegram
```

### Run API only

```bash
uv run main.py --mode api
```

### Run API and Telegram together

```bash
uv run main.py --mode api --mode telegram
```

For full setup instructions, see [Installation](#installation).

## Docker Deployment

### Prerequisites

- Docker
- Docker Compose
- A configured `.env` file

### Build the image

```bash
docker compose build
```

### Run in Telegram mode (default)

```bash
docker compose up -d
```

### Run in CLI mode

```bash
INSTACHEF_MODE=cli docker compose run --rm instachef
```

Stop it with:

```bash
docker compose down
```

### Notes

- `db/` and `downloaded_reels/` are mounted as volumes to persist local data and temporary files.
- The application mode is controlled by repeated `--mode` flags. If omitted, all connectors are started.
- Keep secrets in `.env`; it is not copied into the image.

## Project Overview

The code is organized into three layers:

- `domain/` contains the Pydantic business models.
- `core/` contains the ports and orchestration service.
- `providers/` contains the concrete implementations: LLM extraction, JSON storage, MongoDB storage, reel downloading.
- `connectors/` contains user-facing entry points, currently mostly the CLI.

### Structure

```text
main.py                      CLI entry point
connectors/
  api.py                     FastAPI adapter
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
  mongodb_recipe_repository.py     MongoDB persistence
  reels_downloader.py              Reel download logic
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
6. The result is saved to Supabase, MongoDB, or local JSON storage.
7. The temporary video file is removed.

## Installation

### Requirements

- Python 3.13+
- `uv`
- A Supabase account or MongoDB instance (for data storage)
- A Gemini API key (or another LLM provider)

### Setup

1. **Install dependencies:**

   ```bash
   uv sync
   ```

2. **Configure environment variables** (create a `.env` file):

   ```env
   # AI 
   AI_MODEL=gemini-3.1-flash-lite-preview
   GOOGLE_API_KEY=your-gemini-key

   # Telegram bot
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   TELEGRAM_AUTHORIZED_USER_IDS=123456789,987654321

    # Storage backend
    RECIPE_REPOSITORY_BACKEND=supabase  # or local_json, mongodb
    ## Local JSON
    # LOCAL_JSON_TARGET_DIR=db

    ## Supabase
    SUPABASE_URL=https://your-project.supabase.co
    SUPABASE_KEY=your-anon-key
    
    ## MongoDB
    # MONGODB_URI=mongodb://localhost:27017
    # MONGODB_DATABASE=instachef
    # MONGODB_COLLECTION=recipes
   ```

3. **Configure the storage backend**.

- `supabase`: create the `recipes` table in Supabase.
- `local_json`: no database setup required.
- `mongodb`: no collection setup required, but the database and collection names must be reachable.

### Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase anon key |
| `MONGODB_URI` | Yes for `mongodb` | MongoDB connection string |
| `MONGODB_DATABASE` | No | MongoDB database name (default: `instachef`) |
| `MONGODB_COLLECTION` | No | MongoDB collection name (default: `recipes`) |
| `RECIPE_REPOSITORY_BACKEND` | No | Storage backend (`supabase`, `local_json`, `mongodb`) |
| `LOCAL_JSON_TARGET_DIR` | No | Local JSON directory (default: `db`) |
| `AI_MODEL` | No | Model name (default: `gemini-3.1-flash-lite-preview`) |
| `GOOGLE_API_KEY` | No | Gemini API key (Pydantic AI reads it automatically) |
| `TELEGRAM_BOT_TOKEN` | yes for `--mode telegram` | Telegram bot token |
| `TELEGRAM_AUTHORIZED_USER_IDS` | No | Comma-separated list of allowed Telegram user IDs; leave empty to deny all Telegram access |
| `API_HOST` | No | API bind host (default: `0.0.0.0`) |
| `API_PORT` | No | API port (default: `8000`) |

**Note:** For other AI providers (OpenAI, Anthropic), set `AI_MODEL` to the appropriate model name and ensure the corresponding env var is set (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.). See [Pydantic AI models](https://ai.pydantic.dev/models/overview/).

## Usage

### CLI Mode

```bash
uv run main.py --mode cli
```

1. Enter an Instagram reel URL when prompted
2. The app downloads and processes the reel
3. Recipe data is extracted and saved to Supabase
4. Result is displayed in the terminal
5. Downloaded video is cleaned up

Type `exit` to quit the loop.

### Data Model & Output

Recipes are stored as `RecipeRecord` rows in Supabase, as JSON documents locally, or as documents in MongoDB.

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
