import os
from dataclasses import dataclass, field

from logger import logger

SUPPORTED_REPOSITORY_BACKENDS = {"supabase", "local_json", "mongodb"}


@dataclass(frozen=True)
class AppConfig:
    ai_model: str
    repository_backend: str
    supabase_url: str | None
    supabase_key: str | None
    local_json_target_dir: str
    mongodb_uri: str | None
    mongodb_database: str
    mongodb_collection: str
    telegram_bot_token: str | None
    api_host: str
    api_port: int
    telegram_authorized_user_ids: list[int] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "AppConfig":
        repository_backend = os.getenv("RECIPE_REPOSITORY_BACKEND", "supabase").strip()
        if repository_backend not in SUPPORTED_REPOSITORY_BACKENDS:
            supported = ", ".join(sorted(SUPPORTED_REPOSITORY_BACKENDS))
            logger.error(f"Invalid repository backend: {repository_backend}")
            raise ValueError(f"RECIPE_REPOSITORY_BACKEND must be one of: {supported}")

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if repository_backend == "supabase" and (not supabase_url or not supabase_key):
            logger.error(
                "SUPABASE_URL and SUPABASE_KEY must be set for Supabase backend."
            )
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        mongodb_uri = os.getenv("MONGODB_URI")
        if repository_backend == "mongodb" and not mongodb_uri:
            logger.error("MONGODB_URI must be set for MongoDB backend.")
            raise ValueError("MONGODB_URI must be set")

        return cls(
            ai_model=os.getenv("AI_MODEL", "gemini-3.1-flash-lite-preview").strip(),
            repository_backend=repository_backend,
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            local_json_target_dir=os.getenv("LOCAL_JSON_TARGET_DIR", "db").strip(),
            mongodb_uri=mongodb_uri,
            mongodb_database=os.getenv("MONGODB_DATABASE", "instachef").strip(),
            mongodb_collection=os.getenv("MONGODB_COLLECTION", "recipes").strip(),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            api_host=os.getenv("API_HOST", "0.0.0.0").strip(),
            api_port=int(os.getenv("API_PORT", "8000")),
            telegram_authorized_user_ids=cls._parse_user_ids(
                os.getenv("TELEGRAM_AUTHORIZED_USER_IDS", "")
            ),
        )

    @staticmethod
    def _parse_user_ids(raw_user_ids: str) -> list[int]:
        parsed_ids: list[int] = []
        for token in raw_user_ids.split(","):
            token = token.strip()
            if not token:
                continue
            parsed_ids.append(int(token))
        return parsed_ids
