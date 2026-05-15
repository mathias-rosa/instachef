import asyncio
import re
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    TelegramObject,
)
from aiogram.utils.formatting import Bold, Text

from connectors import CookachuConnector
from core.ports import RecipeRepository
from core.process_reel import ProcessReelService
from domain.exceptions import CookachuError, NotARecipeError
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


class TelegramConnector(CookachuConnector):
    def __init__(
        self,
        reelsProcessingService: ProcessReelService,
        recipeRepository: RecipeRepository,
        token: str,
        authorized_user_ids: set[int],
    ):
        self.reelsProcessingService = reelsProcessingService
        self.recipeRepository = recipeRepository
        self.bot = Bot(token=token)
        self.dispatcher = Dispatcher()
        self.router = Router()

        self.router.message.middleware(
            AuthorizationMiddleware(
                authorized_user_ids=authorized_user_ids,
                allowed_commands={"start", "help", "myid", "recipe", "ids"},
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
                "<b>Mode d'emploi</b>\n\n"
                "<b>Ajouter une recette</b>\n"
                "1. Envoie une URL de Reel Instagram\n"
                "2. Je traite le Reel et extrait la recette\n"
                "3. La recette est enregistrée en base\n\n"
                "<b>Récupérer une recette</b>\n"
                "/ids - Affiche les 10 dernières recettes avec des boutons\n"
                "/recipe &lt;recipe_id&gt; - Affiche une recette par son ID\n"
                "Exemple: <code>/recipe reel:DTpNTQijLaj</code>\n\n"
                "<b>Autres</b>\n"
                "/myid - Voir ton ID Telegram",
                parse_mode="HTML",
            )

        @self.router.message(Command("myid"))
        async def myid_handler(message: Message) -> None:
            user_id = message.from_user.id if message.from_user else "inconnu"
            await message.answer(f"Ton Telegram user id: {user_id}")

        @self.router.message(Command("recipe"))
        async def recipe_handler(message: Message) -> None:
            text = (message.text or "").strip()
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                await message.answer(
                    "Usage: /recipe <recipe_id>\n\n"
                    "Exemple: /recipe cookachu__DTpNTQijLaj"
                )
                return

            recipe_id = parts[1].strip()
            if not recipe_id:
                await message.answer(
                    "Usage: /recipe <recipe_id>\n\n"
                    "Exemple: /recipe cookachu__DTpNTQijLaj"
                )
                return

            waiting_message = await message.answer("Récupération de la recette...")

            try:
                record = await asyncio.to_thread(
                    self.recipeRepository.find_by_id,
                    recipe_id,
                )
                if not record:
                    await waiting_message.edit_text(
                        f"❌ Recette avec l'ID '{recipe_id}' non trouvée."
                    )
                    return

                recipe_html = self._format_recipe_html(record)
                await waiting_message.edit_text(recipe_html, parse_mode="HTML")
            except Exception as exc:
                logger.error(f"Error retrieving recipe {recipe_id}: {exc}")
                await waiting_message.edit_text(f"❌ Erreur: {exc}")

        @self.router.message(Command("ids"))
        async def ids_handler(message: Message) -> None:
            waiting_message = await message.answer("Récupération des recettes...")

            try:
                records = await asyncio.to_thread(
                    self.recipeRepository.get_recent_recipes,
                    10,
                )
                if not records:
                    await waiting_message.edit_text(
                        "Aucune recette enregistrée pour le moment."
                    )
                    return

                keyboard = self._build_recipes_keyboard(records)
                await waiting_message.edit_text(
                    "<b>📚 Recettes récentes</b>\n\nClique pour afficher une recette:",
                    parse_mode="HTML",
                    reply_markup=keyboard,
                )
            except Exception as exc:
                logger.error(f"Error listing recipes: {exc}")
                await waiting_message.edit_text(f"❌ Erreur: {exc}")

        @self.router.callback_query(lambda c: c.data and c.data.startswith("recipe:"))
        async def recipe_callback_handler(callback_query: CallbackQuery) -> None:
            try:
                if not callback_query.data:
                    await callback_query.answer(
                        "❌ Erreur: données manquantes", show_alert=True
                    )
                    return

                recipe_id = callback_query.data.replace("recipe:", "", 1)
                record = await asyncio.to_thread(
                    self.recipeRepository.find_by_id,
                    recipe_id,
                )

                if not record:
                    await callback_query.answer(
                        "❌ Recette non trouvée",
                        show_alert=True,
                    )
                    return

                recipe_html = self._format_recipe_html(record)
                # Update the message with the recipe
                if callback_query.message:
                    # Type: ignore because the type checker can't guarantee message has edit_text
                    await callback_query.message.edit_text(  # type: ignore
                        recipe_html,
                        parse_mode="HTML",
                    )
                await callback_query.answer()
            except Exception as exc:
                logger.error(f"Error in recipe callback: {exc}")
                await callback_query.answer(
                    f"❌ Erreur: {exc}",
                    show_alert=True,
                )

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
            except CookachuError as exc:
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
            return await asyncio.to_thread(
                self.reelsProcessingService.execute, reel_url
            )
        except NotARecipeError:
            raise
        except CookachuError:
            raise
        except Exception as exc:
            logger.error(f"Unexpected error processing reel: {exc}")
            raise

    @staticmethod
    def _extract_reel_url(text: str) -> str | None:
        match = INSTAGRAM_REEL_URL_PATTERN.search(text)
        if not match:
            return None
        return match.group(0)

    @staticmethod
    def _format_recipe_html(record: RecipeRecord) -> str:
        """Format recipe as beautiful HTML for Telegram."""
        recipe = record.recipe

        # Header with title and description
        lines = [
            f"<b>{recipe.title}</b>",
            f"<i>{recipe.description}</i>",
            "",
        ]

        # Info section
        info_parts = []
        if recipe.difficulty:
            info_parts.append(f"<b>Difficulté:</b> {recipe.difficulty.value}")
        if recipe.dish_type:
            info_parts.append(f"<b>Type:</b> {recipe.dish_type.value}")
        if recipe.cuisine_type:
            info_parts.append(f"<b>Cuisine:</b> {recipe.cuisine_type.value}")
        if recipe.servings:
            info_parts.append(f"<b>Portions:</b> {recipe.servings} pers.")

        lines.extend(info_parts)
        lines.append("")

        # Timing section
        timings = []
        if recipe.prep_time_minutes:
            timings.append(f"⏱️ Prép: {recipe.prep_time_minutes}min")
        if recipe.cook_time_minutes:
            timings.append(f"🔥 Cuisson: {recipe.cook_time_minutes}min")
        if recipe.rest_time_minutes:
            timings.append(f"💤 Repos: {recipe.rest_time_minutes}min")
        if timings:
            lines.append(" | ".join(timings))
            lines.append("")

        # Ingredients section
        lines.append("<b>🥘 Ingrédients</b>")
        if recipe.ingredients:
            for ing in recipe.ingredients:
                if ing.group:
                    lines.append(f"  <u>{ing.group}</u>")
                qty = ""
                if ing.quantity is not None and ing.unit:
                    qty = f"{ing.quantity} {ing.unit}"
                elif ing.count is not None:
                    qty = f"{ing.count} x"
                ing_line = f"  • {ing.name}"
                if qty:
                    ing_line += f" - {qty}"
                if ing.note:
                    ing_line += f" ({ing.note})"
                lines.append(ing_line)
        lines.append("")

        # Instructions section
        lines.append("<b>👨‍🍳 Préparation</b>")
        if recipe.instructions:
            for idx, step in enumerate(recipe.instructions, 1):
                if step.title:
                    lines.append(f"<b>Étape {idx}: {step.title}</b>")
                else:
                    lines.append(f"<b>Étape {idx}</b>")
                lines.append(f"  {step.description}")
        lines.append("")

        # Tags
        if recipe.tags:
            tags_str = " ".join(f"#{tag}" for tag in recipe.tags)
            lines.append(f"<code>{tags_str}</code>")
            lines.append("")

        # Tips
        if recipe.tips:
            lines.append("<b>💡 Astuces</b>")
            for tip in recipe.tips:
                lines.append(f"  • {tip}")
            lines.append("")

        # Appliances/Utensils
        tools = []
        if recipe.appliances:
            tools.append(f"Appareils: {', '.join(a.value for a in recipe.appliances)}")
        if recipe.utensils:
            tools.append(f"Ustensiles: {', '.join(recipe.utensils)}")
        if tools:
            lines.append("<b>🔧 Équipement</b>")
            for tool in tools:
                lines.append(f"  • {tool}")
            lines.append("")

        # Source
        source_info = record.source.canonical_id()
        lines.append(f"<code>ID: {source_info}</code>")

        return "\n".join(lines)

    @staticmethod
    def _build_recipes_keyboard(records: list[RecipeRecord]) -> InlineKeyboardMarkup:
        """Build inline keyboard with recipe titles as buttons."""
        buttons = []
        for record in records:
            recipe = record.recipe
            # Limit title to 20 chars for display, use full ID as callback
            btn_text = (
                recipe.title[:20] + "..." if len(recipe.title) > 20 else recipe.title
            )
            callback_data = f"recipe:{record.id}"
            buttons.append(
                InlineKeyboardButton(
                    text=btn_text,
                    callback_data=callback_data,
                )
            )

        # Arrange buttons in 2 columns
        keyboard = []
        for i in range(0, len(buttons), 2):
            row = buttons[i : i + 2]
            keyboard.append(row)

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    async def run(self) -> None:
        logger.info("Starting Telegram bot polling...")
        await self.dispatcher.start_polling(self.bot)
