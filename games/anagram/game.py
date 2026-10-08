"""
Anagramma: Aralashtirilgan harflardan so'z topish o'yini.
"""

from __future__ import annotations

import logging
import random
from pathlib import Path

from core.base import BaseGame
from core.storage import game_store
from core.ui import button, delete_user_message, home_button, show

from . import texts

log = logging.getLogger(__name__)

GAME_ID = "anagram"
WORDS_PATH = Path(__file__).with_name("words.txt")


class AnagramGame(BaseGame):
    id = GAME_ID
    title = "🔤 Anagramma"
    order = 30

    def __init__(self) -> None:
        self.words: list[str] = []

    def on_load(self) -> None:
        if WORDS_PATH.exists():
            with open(WORDS_PATH, "r", encoding="utf-8") as f:
                self.words = [line.strip().lower() for line in f if line.strip() and not line.startswith("#")]
        log.info("Anagramma: %d ta so'z yuklandi.", len(self.words))

    def _st(self, context) -> dict:
        return game_store(context.user_data, self.id)

    def _get_scrambled(self, word: str) -> str:
        chars = list(word)
        while True:
            random.shuffle(chars)
            scrambled = "".join(chars)
            if scrambled != word and len(word) > 1:
                return " - ".join(chars) # Harflarni chiziqcha bilan ajratib ko'rsatamiz

    def _start_new_word(self, st: dict) -> bool:
        if not self.words:
            return False
        word = random.choice(self.words)
        st["secret"] = word
        st["scrambled"] = self._get_scrambled(word)
        return True

    async def _home(self, update, context, notice: str | None = None) -> None:
        st = self._st(context)
        rows = [
            [button("▶️ Yangi so'z", f"g:{self.id}:new")],
            [button("📖 Qoidalar", f"g:{self.id}:rules"), button("📊 Statistika", f"g:{self.id}:stats")],
            [button("⬅️ Orqaga", "sec:games"), home_button()],
        ]
        text = texts.home(st.get("wins", 0), st.get("losses", 0), notice)
        await show(update, context, text, rows)

    async def _play(self, update, context, notice: str | None = None) -> None:
        st = self._st(context)
        if not st.get("secret"):
            if not self._start_new_word(st):
                await self._home(update, context, notice="So'zlar bazasi bo'sh!")
                return

        rows = [
            [button("⏭ Boshqa so'z", f"g:{self.id}:skip"), button("📖 Qoidalar", f"g:{self.id}:rules")],
            [button("⬅️ Orqaga", "sec:games"), home_button()],
        ]
        text = texts.play(st.get("scrambled", ""), st.get("wins", 0), notice)
        await show(update, context, text, rows)

    async def _back(self, update, context) -> None:
        if self._st(context).get("secret"):
            await self._play(update, context)
        else:
            await self._home(update, context)

    async def on_open(self, update, context) -> None:
        await self._back(update, context)

    async def on_callback(self, update, context, action: str) -> None:
        st = self._st(context)

        if action == "home":
            await self._home(update, context)
        elif action == "back":
            await self._back(update, context)
        elif action == "new" or action == "skip":
            if action == "skip" and st.get("secret"):
                st["losses"] = st.get("losses", 0) + 1
            self._start_new_word(st)
            await self._play(update, context)
        elif action == "rules":
            rows = [[button("⬅️ Orqaga", f"g:{self.id}:back"), home_button()]]
            await show(update, context, texts.rules(), rows)
        elif action == "stats":
            rows = [[button("⬅️ Orqaga", f"g:{self.id}:back"), home_button()]]
            await show(update, context, texts.stats(st.get("wins", 0), st.get("losses", 0)), rows)
        else:
            await self._back(update, context)

    async def on_text(self, update, context) -> None:
        await delete_user_message(update)
        st = self._st(context)
        secret = st.get("secret")
        if not secret:
            await self._home(update, context, notice="Avval ▶️ Yangi so'z tugmasini bosing.")
            return

        user_text = (update.message.text or "").strip().lower()

        if user_text == secret:
            st["wins"] = st.get("wins", 0) + 1
            self._start_new_word(st)
            await self._play(update, context, notice=f"🎉 To'g'ri! Oldingi so'z: <b>{secret}</b> idi.")
        else:
            await self._play(update, context, notice=f"❌ Noto'g'ri, qaytadan urinib ko'ring!")


GAME = AnagramGame()