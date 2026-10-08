"""
Bosh menyu va yo'naltirish. Bu fayl o'yinlar haqida hech narsa bilmaydi,
hammasini registry orqali topadi.
"""

from __future__ import annotations

import html
import logging

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from . import registry
from .ui import button, delete_user_message, show

log = logging.getLogger(__name__)


def _esc(s: str) -> str:
    return html.escape(s, quote=False)


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, *, intro: str | None = None,
                    notice: str | None = None, force_new: bool = False) -> None:
    """Bosh menyuni ko'rsatadi. intro - HTML tayyor matn (salom), notice - oddiy matn (ogohlantirish)."""
    context.user_data["mode"] = None
    if registry.SECTIONS:
        body = "🏠 <b>Bosh menyu</b>\n\nBo'limni tanlang:"
    else:
        body = "🏠 <b>Bosh menyu</b>\n\nHozircha bo'limlar yo'q."
    parts = []
    if intro:
        parts.append(intro)
    if notice:
        parts.append(f"⚠️ {_esc(notice)}")
    parts.append(body)
    rows = [[button(s.title, f"sec:{s.id}")] for s in registry.SECTIONS.values()]
    await show(update, context, "\n\n".join(parts), rows, force_new=force_new)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = _esc(update.effective_user.first_name or "do'st")
    await main_menu(update, context, intro=f"👋 Salom, {name}!", force_new=True)


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    parts = (query.data or "").split(":", 2)
    kind = parts[0]
    ud = context.user_data

    if kind == "menu":
        await main_menu(update, context)
        return

    if kind == "sec" and len(parts) >= 2:
        section = registry.SECTIONS.get(parts[1])
        ud["mode"] = None
        if section is None:
            await main_menu(update, context, notice="Bu bo'lim topilmadi.")
            return
        await section.show(update, context)
        return

    if kind == "g" and len(parts) >= 2:
        game = registry.GAMES.get(parts[1])
        if game is None:
            await main_menu(update, context, notice="Bu o'yin topilmadi.")
            return
        action = parts[2] if len(parts) > 2 else "open"
        ud["mode"] = game.id
        if action == "open":
            await game.on_open(update, context)
        else:
            await game.on_callback(update, context, action)
        return

    await main_menu(update, context)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Yozilgan matn hozir ochiq turgan o'yinga beriladi. O'yin ochiq bo'lmasa, menyu chiqadi."""
    mode = context.user_data.get("mode")
    game = registry.GAMES.get(mode) if mode else None
    if game is not None:
        await game.on_text(update, context)
        return
    await delete_user_message(update)
    await main_menu(update, context, notice="Avval menyudan bo'lim tanlang 👇")


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.error("Xatolik yuz berdi", exc_info=context.error)
    if isinstance(update, Update) and update.effective_chat is not None:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Kutilmagan xatolik yuz berdi. /start ni bosib qayta urinib ko'ring.",
            )
        except Exception:
            pass


def register(app: Application) -> None:
    app.add_handler(CommandHandler(["start", "menu"], cmd_start))
    app.add_handler(CallbackQueryHandler(on_callback, pattern=r"^(menu|sec|g)(:|$)"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_error_handler(on_error)
