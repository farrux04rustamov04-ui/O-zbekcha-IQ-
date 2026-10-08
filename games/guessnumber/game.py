"""
Sonni top: 1 dan 100 gacha bo'lgan sonni topish o'yini.
"""

from __future__ import annotations

import logging
import random

from core.base import BaseGame
from core.storage import game_store
from core.ui import button, delete_user_message, home_button, show

from . import texts

log = logging.getLogger(__name__)

GAME_ID = "guessnumber"


class GuessNumber(BaseGame):
    id = GAME_ID
    title = "🔢 Sonni top"
    order = 20

    def on_load(self) -> None:
        log.info("Sonni top o'yini yuklandi.")

    def _st(self, context) -> dict:
        return game_store(context.user_data, self.id)

    def _start_new(self, st: dict) -> None:
        st["secret"] = random.randint(1, 100)
        st["attempts"] = 0
        st["last_guess"] = None
        st["hint"] = None

    async def _home(self, update, context, notice: str | None = None) -> None:
        st = self._st(context)
        rows = [
            [button("▶️ Yangi o'yin", f"g:{self.id}:new")],
            [button("📖 Qoidalar", f"g:{self.id}:rules"), button("📊 Statistika", f"g:{self.id}:stats")],
            [button("⬅️ Orqaga", "sec:games"), home_button()],
        ]
        text = texts.home(st.get("wins", 0), st.get("losses", 0), notice)
        await show(update, context, text, rows)

    async def _play(self, update, context, notice: str | None = None) -> None:
        st = self._st(context)
        rows = [
            [button("🏳️ Taslim bo'lish", f"g:{self.id}:giveup"), button("📖 Qoidalar", f"g:{self.id}:rules")],
            [button("⬅️ Orqaga", "sec:games"), home_button()],
        ]
        text = texts.play(
            st.get("attempts", 0), 
            st.get("last_guess"), 
            st.get("hint"), 
            notice
        )
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
        elif action == "new":
            self._start_new(st)
            await self._play(update, context)
        elif action == "rules":
            rows = [[button("⬅️ Orqaga", f"g:{self.id}:back"), home_button()]]
            await show(update, context, texts.rules(), rows)
        elif action == "stats":
            rows = [[button("⬅️ Orqaga", f"g:{self.id}:back"), home_button()]]
            await show(update, context, texts.stats(st.get("wins", 0), st.get("losses", 0), st.get("best")), rows)
        elif action == "giveup":
            secret = st.pop("secret", None)
            st.pop("attempts", None)
            st.pop("last_guess", None)
            st.pop("hint", None)
            if secret is not None:
                st["losses"] = st.get("losses", 0) + 1
            await self._home(update, context, notice=f"Taslim bo'ldingiz. O'ylangan son: {secret}")
        else:
            await self._back(update, context)

    async def on_text(self, update, context) -> None:
        await delete_user_message(update)
        st = self._st(context)
        secret = st.get("secret")
        if secret is None:
            await self._home(update, context, notice="Avval ▶️ Yangi o'yin tugmasini bosing.")
            return

        text = update.message.text or ""
        if not text.isdigit():
            await self._play(update, context, notice="Iltimos, faqat butun son kiriting!")
            return

        guess = int(text)
        attempts = st.get("attempts", 0) + 1
        st["attempts"] = attempts
        st["last_guess"] = guess

        if guess < secret:
            st["hint"] = f"O'ylangan son {guess} dan KATTA 📈"
            await self._play(update, context)
        elif guess > secret:
            st["hint"] = f"O'ylangan son {guess} dan KICHIK 📉"
            await self._play(update, context)
        else:
            st.pop("secret", None)
            st.pop("attempts", None)
            st.pop("last_guess", None)
            st.pop("hint", None)
            st["wins"] = st.get("wins", 0) + 1
            best = st.get("best")
            if best is None or attempts < best:
                st["best"] = attempts

            rows = [
                [button("▶️ Yangi o'yin", f"g:{self.id}:new")],
                [button("⬅️ Orqaga", "sec:games"), home_button()],
            ]
            text_res = texts.finished(secret, attempts, st.get("wins", 0), st.get("losses", 0))
            await show(update, context, text_res, rows)


GAME = GuessNumber()