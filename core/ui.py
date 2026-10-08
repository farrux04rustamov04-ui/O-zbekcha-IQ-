"""
Ekran chizish yordamchilari.

show() botning bitta xabarini tahrirlab turadi (chat to'lib ketmaydi):
  - tugma bosilganda - o'sha xabar tahrirlanadi;
  - matn yozilganda  - botning oxirgi ekran xabari tahrirlanadi;
  - tahrirlab bo'lmasa (xabar o'chib ketgan va h.k.) - yangi xabar yuboriladi.
Matn HTML formatida (<b>, <i>, <code>) yuboriladi. Foydalanuvchi matnini html.escape() qiling.
"""

from __future__ import annotations

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest, TelegramError
from telegram.ext import ContextTypes

log = logging.getLogger(__name__)


def button(text: str, data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text, callback_data=data)


def home_button() -> InlineKeyboardButton:
    return button("🏠 Bosh menyu", "menu:main")


def _markup(rows):
    return InlineKeyboardMarkup(rows) if rows else None


async def _clear_markup(bot, chat_id: int, message_id: int) -> None:
    try:
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
    except TelegramError:
        pass


async def delete_user_message(update: Update) -> None:
    """Foydalanuvchi yozgan xabarni o'chiradi (chat toza turishi uchun). Bo'lmasa, jim o'tadi."""
    try:
        if update.message is not None:
            await update.message.delete()
    except TelegramError:
        pass


async def show(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, rows=None, *, force_new: bool = False) -> None:
    ud = context.user_data
    chat_id = update.effective_chat.id
    kb = _markup(rows)
    query = update.callback_query

    if not force_new:
        if query is not None and query.message is not None:
            # Tugma bosildi: shu xabarni tahrirlaymiz
            try:
                await query.edit_message_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
                ud["screen"] = [chat_id, query.message.message_id]
                return
            except BadRequest as e:
                if "not modified" in str(e).lower():
                    ud["screen"] = [chat_id, query.message.message_id]
                    return
                log.warning("Xabarni tahrirlab bo'lmadi: %s", e)
            except TelegramError as e:
                log.warning("Xabarni tahrirlab bo'lmadi: %s", e)
        elif query is None:
            # Matn yozildi: botning oxirgi ekranini tahrirlaymiz
            ref = ud.get("screen")
            if ref and ref[0] == chat_id:
                try:
                    await context.bot.edit_message_text(
                        chat_id=ref[0], message_id=ref[1], text=text,
                        reply_markup=kb, parse_mode=ParseMode.HTML,
                    )
                    return
                except BadRequest as e:
                    if "not modified" in str(e).lower():
                        return
                except TelegramError:
                    pass

    # Yangi xabar yuboramiz, eskisining tugmalarini olib tashlaymiz
    old = ud.get("screen")
    msg = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=kb, parse_mode=ParseMode.HTML)
    if old and old[0] == chat_id and old[1] != msg.message_id:
        await _clear_markup(context.bot, old[0], old[1])
    ud["screen"] = [chat_id, msg.message_id]
