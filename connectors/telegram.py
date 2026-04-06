import asyncio
import re
from collections.abc import Awaitable, Callable
from typing import Any, cast

from aiogram import BaseMiddleware, Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message, TelegramObject
from aiogram.utils.formatting import Bold, Text

from connectors import InstachefConnector
from core.process_reel import ProcessReelService
from domain.exceptions import InstachefError, NotARecipeError
from domain.recipe_record import RecipeRecord
from logger import logger

INSTAGRAM_REEL_URL_PATTERN = re.compile(
    r"https?://(?:www\.)?instagram\.com/reel/[A-Za-z0-9_-]+/?(?:\?[\S]*)?",
    re.IGNORECASE,
)


class AuthorizationMiddleware(BaseMiddleware):
    def __init__(
        self,
        authorized_user_ids: set[int],
        allowed_commands: set[str] | None = None,
    ) -> None:
        self.authorized_user_ids = authorized_user_ids
        self.allowed_commands = allowed_commands or set()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:

        if not isinstance(event, Message):
            return await handler(event, data)

        if not self.authorized_user_ids:
            await event.answer("Accès refusé. Vous n'êtes pas autorisé.")
            return None

        user = event.from_user
        if not user:
            return None

        if user.id in self.authorized_user_ids:
            return await handler(event, data)

        text = (event.text or "").strip()
        command = self._extract_command(text)
        if command and command in self.allowed_commands:
            return await handler(event, data)

        await event.answer("Accès refusé. Vous n'êtes pas autorisé.")
        return None

    @staticmethod
    def _extract_command(text: str) -> str | None:
        if not text.startswith("/"):
            return None
        token = text.split(maxsplit=1)[0]
        return token.split("@", maxsplit=1)[0][1:].lower()


class TelegramConnector(InstachefConnector):
    def __init__(
        self,
        service: ProcessReelService,
        token: str,
        authorized_user_ids: set[int],
    ):
        self.service = service
        self.bot = Bot(token=token)
        self.dispatcher = Dispatcher()
        self.router = Router()

        self.router.message.middleware(
            AuthorizationMiddleware(
                authorized_user_ids=authorized_user_ids,
                allowed_commands={"start", "help", "myid"},
            )
        )
        self.dispatcher.include_router(self.router)
        self._register_handlers()

    def _register_handlers(self) -> None:
        @self.router.message(Command("start"))
        async def start_handler(message: Message) -> None:
            await message.answer(
                "Salut ! Envoie-moi une URL de Reel Instagram pour l'extraire et l'enregistrer en base de données. Tape /help pour plus d'instructions."
            )

        @self.router.message(Command("help"))
        async def help_handler(message: Message) -> None:
            await message.answer(
                "Mode d'emploi:\n"
                "1) Envoie une URL de Reel Instagram\n"
                "2) Je traite le Reel\n"
                "3) Je confirme si c'est enregistré en base"
            )

        @self.router.message(Command("myid"))
        async def myid_handler(message: Message) -> None:
            user_id = message.from_user.id if message.from_user else "inconnu"
            await message.answer(f"Ton Telegram user id: {user_id}")

        @self.router.message()
        async def reel_handler(message: Message) -> None:
            text = (message.text or "").strip()
            if not text:
                await message.answer(
                    "Envoie un message texte contenant une URL de Reel."
                )
                return

            reel_url = self._extract_reel_url(text)
            if not reel_url:
                await message.answer("Je n'ai pas trouvé d'URL Reel valide 🥲")
                return

            waiting_message = await message.answer(
                "Traitement en cours, ça peut prendre quelques secondes..."
            )

            try:
                record = await self._process_reel(reel_url)
            except NotARecipeError:
                await waiting_message.edit_text(
                    "Ce Reel ne contient pas de recette valide. Envoie un autre Reel ! 👨‍🍳"
                )
                return
            except InstachefError as exc:
                await waiting_message.edit_text(f"Erreur: {exc}")
                return

            recipe = record.recipe

            response = Text(
                Bold(recipe.title),
                "\n\n",
                recipe.description or "",
                "\n\n✅ Enregistré en base",
            )
            await waiting_message.edit_text(response.as_html(), parse_mode="HTML")

    async def _process_reel(self, reel_url: str) -> RecipeRecord:
        try:
            return cast(
                RecipeRecord,
                await asyncio.to_thread(self.service.execute, reel_url),
            )
        except NotARecipeError:
            raise
        except InstachefError:
            raise
        except Exception as exc:
            logger.error(f"Telegram bot reel processing error: {exc}")
            raise

    @staticmethod
    def _extract_reel_url(text: str) -> str | None:
        match = INSTAGRAM_REEL_URL_PATTERN.search(text)
        if not match:
            return None
        return match.group(0)

    async def run(self) -> None:
        logger.info("Starting Telegram bot polling...")
        await self.dispatcher.start_polling(self.bot)
