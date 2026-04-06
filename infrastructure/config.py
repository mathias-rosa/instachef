import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AppConfig:
    supabase_url: str
    supabase_key: str
    ai_model: str
    telegram_bot_token: str | None
    telegram_authorized_user_ids: list[int] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "AppConfig":
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        return cls(
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            ai_model=os.getenv("AI_MODEL", "gemini-3.1-flash-lite-preview").strip(),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
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
