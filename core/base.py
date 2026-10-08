"""
Har bir o'yin va har bir bosh menyu bo'limi shu sinflardan meros oladi.

YANGI O'YIN: games/<nom>/game.py faylida BaseGame dan meros oluvchi sinf yozing
va fayl oxirida   GAME = SizningSinf()   deb e'lon qiling. Boshqa hech narsa kerak emas,
yadro papkani o'zi topadi va tugmani "O'yinlar" ro'yxatiga qo'shadi.

YANGI BO'LIM: sections/<nom>.py faylida Section dan meros oluvchi sinf yozing
va oxirida   SECTION = SizningSinf()   deb e'lon qiling.

Tugma (callback_data) formati:
    menu:main                -> bosh menyu
    sec:<bo'lim_id>          -> bo'limni ochish
    g:<o'yin_id>:<amal>      -> o'yin tugmasi ("open" amali - o'yinni ochish)
"""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


class BaseGame:
    id: str = ""      # noyob nom, masalan "word500" (callback_data da ishlatiladi, ":" bo'lmasin)
    title: str = ""   # "O'yinlar" ro'yxatidagi tugma yozuvi
    order: int = 100  # ro'yxatdagi tartib (kichigi yuqorida)

    def on_load(self) -> None:
        """Bot ishga tushganda bir marta chaqiriladi (masalan, so'zlarni yuklash).
        Xato chiqarsa, o'yin ro'yxatga qo'shilmaydi, qolgan bot ishlayveradi."""

    async def on_open(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Foydalanuvchi o'yinni ro'yxatdan tanlaganda chaqiriladi."""
        raise NotImplementedError

    async def on_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
        """O'yin ichidagi tugma bosilganda chaqiriladi (g:<id>:<action>)."""

    async def on_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Foydalanuvchi o'yin ichida matn yozganda chaqiriladi (masalan, so'z taxmini)."""


class Section:
    id: str = ""
    title: str = ""
    order: int = 100

    async def show(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        raise NotImplementedError
