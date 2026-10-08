"""
So'zni top (Word 500): 5 harfli yashirin so'z, 8 urinish.
Har bir taxmindan keyin: nechta harf to'g'ri joyda (🟩), nechtasi noto'g'ri joyda (🟨),
nechtasi so'zda yo'q (🟥). Qaysi harflar ekanini bot aytmaydi.

Uchta yordam (har biri uchun alohida hamyon, hamyon o'yinlar orasida umumiy):
  💡 Maslahat    - words.txt da yozilgan maslahatlar birma-bir ochiladi
  🔤 Harf ochish - bitta harf o'z joyi bilan ochiladi (bir o'yinda ko'pi bilan 4 ta)
  🚫 Yo'q unli   - so'zda yo'q unlilardan biri ko'rsatiladi
Hamyon 10 dan boshlanadi, har g'alabada har biriga +1 (ko'pi bilan 20).
Foydasiz bosilgan yordam (ochiladigan narsa qolmagan) hamyondan ayirilmaydi.
"""

from __future__ import annotations

import logging
import random
from collections import Counter
from pathlib import Path

from core.base import BaseGame
from core.storage import game_store
from core.ui import button, delete_user_message, home_button, show
from shared import uzbek

from . import texts

log = logging.getLogger(__name__)

# DIQQAT: GAME_ID ni o'zgartirmang. Foydalanuvchilar statistikasi shu nom ostida saqlanadi.
GAME_ID = "word500"
WORD_LENGTH = 5
MAX_ATTEMPTS = 8
WORDS_PATH = Path(__file__).with_name("words.txt")

START_WALLET = 10
MAX_WALLET = 20
MAX_LETTER_REVEALS = 4
VOWELS = ["a", "e", "i", "o", "o'", "u"]
HELP_KEYS = ("hint", "letter", "vowel")


def score(secret: list[str], guess: list[str]) -> tuple[int, int, int]:
    """(to'g'ri joyda, noto'g'ri joyda, so'zda yo'q) harflar soni."""
    green = sum(s == g for s, g in zip(secret, guess))
    common = sum((Counter(secret) & Counter(guess)).values())
    yellow = common - green
    red = len(secret) - green - yellow
    return green, yellow, red


class Word500(BaseGame):
    id = GAME_ID
    title = f"🔤 {texts.GAME_NAME}"
    order = 10

    def __init__(self) -> None:
        self.words: list[list[str]] = []
        self.hints: dict[tuple[str, ...], list[str]] = {}

    # ---------- yuklash ----------

    def on_load(self) -> None:
        entries, problems = uzbek.load_word_entries(WORDS_PATH, WORD_LENGTH)
        for p in problems:
            log.warning("words.txt: %s", p)
        if not entries:
            raise RuntimeError("words.txt da bitta ham yaroqli so'z yo'q")
        self.words = [tokens for tokens, _ in entries]
        self.hints = {tuple(tokens): hints for tokens, hints in entries if hints}
        log.info(
            "%s: %d ta so'z yuklandi (%d tasida maslahat bor), %d ta xato qator.",
            texts.GAME_NAME, len(self.words), len(self.hints), len(problems),
        )

    # ---------- yordamchilar ----------

    def _st(self, context) -> dict:
        return game_store(context.user_data, self.id)

    @staticmethod
    def _wallet(st: dict) -> dict:
        """Yordam hamyoni. Eski foydalanuvchilarda yo'q bo'lsa, 10 tadan beriladi."""
        wallet = st.setdefault("wallet", {})
        for key in HELP_KEYS:
            wallet.setdefault(key, START_WALLET)
        return wallet

    @staticmethod
    def _lines(history: list[dict]) -> list[str]:
        return [
            texts.history_line(i, uzbek.show_word(h["t"], spaced=True), h["g"], h["y"], h["r"])
            for i, h in enumerate(history, 1)
        ]

    @staticmethod
    def _reset_round(st: dict) -> None:
        st["hints_shown"] = 0
        st["revealed"] = []
        st["absent"] = []

    def _start_new(self, st: dict) -> None:
        st["secret"] = list(random.choice(self.words))
        st["history"] = []
        self._reset_round(st)

    def _helps_block(self, st: dict) -> str:
        """Ekran tepasida turadigan ochilgan yordamlar."""
        secret = st.get("secret") or []
        parts: list[str] = []

        hints = self.hints.get(tuple(secret), [])
        shown = min(st.get("hints_shown", 0), len(hints))
        if shown:
            parts.append(texts.hints_block(hints[:shown], len(hints)))

        revealed = st.get("revealed", [])
        if revealed:
            cells = [
                uzbek.show_word([secret[i]]) if i in revealed else "_"
                for i in range(len(secret))
            ]
            parts.append(texts.letters_line(cells))

        absent = st.get("absent", [])
        if absent:
            parts.append(texts.absent_line([v.upper() for v in absent]))

        return "\n".join(parts)

    # ---------- ekranlar ----------

    async def _home(self, update, context, notice: str | None = None) -> None:
        st = self._st(context)
        rows = [
            [button("▶️ Yangi o'yin", f"g:{self.id}:new")],
            [button("📖 Qoidalar", f"g:{self.id}:rules"), button("📊 Statistika", f"g:{self.id}:stats")],
            [button("⬅️ Orqaga", "sec:games"), home_button()],
        ]
        text = texts.home(
            WORD_LENGTH, MAX_ATTEMPTS, st.get("wins", 0), st.get("losses", 0), self._wallet(st), notice
        )
        await show(update, context, text, rows)

    async def _play(self, update, context, notice: str | None = None) -> None:
        st = self._st(context)
        history = st.get("history", [])
        wallet = self._wallet(st)
        rows = [
            [
                button(f"💡 Maslahat ({wallet['hint']})", f"g:{self.id}:hint"),
                button(f"🔤 Harf ochish ({wallet['letter']})", f"g:{self.id}:letter"),
            ],
            [button(f"🚫 Yo'q unli ({wallet['vowel']})", f"g:{self.id}:vowel")],
            [button("🏳️ Taslim bo'lish", f"g:{self.id}:giveup"), button("📖 Qoidalar", f"g:{self.id}:rules")],
            [button("⬅️ Orqaga", "sec:games"), home_button()],
        ]
        text = texts.play(
            self._helps_block(st), self._lines(history), MAX_ATTEMPTS - len(history), WORD_LENGTH, notice
        )
        await show(update, context, text, rows)

    async def _back(self, update, context) -> None:
        """O'yin davom etayotgan bo'lsa - o'yin ekrani, aks holda o'yinning bosh ekrani."""
        if self._st(context).get("secret"):
            await self._play(update, context)
        else:
            await self._home(update, context)

    async def _finish(self, update, context, *, won: bool, gave_up: bool = False) -> None:
        st = self._st(context)
        wallet = self._wallet(st)
        secret = st.pop("secret", None) or []
        history = st.pop("history", [])
        for key in ("hints_shown", "revealed", "absent"):
            st.pop(key, None)
        lines = self._lines(history)

        bonus = False
        if won:
            st["wins"] = st.get("wins", 0) + 1
            best = st.get("best")
            if best is None or len(history) < best:
                st["best"] = len(history)
            for key in HELP_KEYS:  # har g'alabada har bir yordamga +1 (ko'pi bilan MAX_WALLET)
                if wallet[key] < MAX_WALLET:
                    wallet[key] += 1
                    bonus = True
        else:
            st["losses"] = st.get("losses", 0) + 1

        text = texts.finished(
            lines, uzbek.show_word(secret), won, gave_up, len(history),
            st.get("wins", 0), st.get("losses", 0), bonus,
        )
        rows = [
            [button("▶️ Yangi o'yin", f"g:{self.id}:new")],
            [button("⬅️ Orqaga", "sec:games"), home_button()],
        ]
        await show(update, context, text, rows)

    # ---------- yordamlar ----------

    async def _use_hint(self, update, context) -> None:
        st = self._st(context)
        wallet = self._wallet(st)
        hints = self.hints.get(tuple(st["secret"]), [])
        shown = st.get("hints_shown", 0)
        notice = None
        if not hints:
            notice = "Bu so'z uchun maslahat yo'q."
        elif shown >= len(hints):
            notice = "Bu so'zning barcha maslahatlari ochilgan."
        elif wallet["hint"] <= 0:
            notice = "Maslahat hamyoningiz bo'sh. Har g'alabada +1 qo'shiladi."
        else:
            st["hints_shown"] = shown + 1
            wallet["hint"] -= 1
        await self._play(update, context, notice)

    async def _use_letter(self, update, context) -> None:
        st = self._st(context)
        wallet = self._wallet(st)
        secret = st["secret"]
        revealed = st.setdefault("revealed", [])
        free = [i for i in range(len(secret)) if i not in revealed]
        notice = None
        if len(revealed) >= MAX_LETTER_REVEALS or not free:
            notice = f"Bu o'yinda boshqa harf ochilmaydi (ko'pi bilan {MAX_LETTER_REVEALS} ta)."
        elif wallet["letter"] <= 0:
            notice = "Harf ochish hamyoningiz bo'sh. Har g'alabada +1 qo'shiladi."
        else:
            revealed.append(random.choice(free))
            wallet["letter"] -= 1
        await self._play(update, context, notice)

    async def _use_vowel(self, update, context) -> None:
        st = self._st(context)
        wallet = self._wallet(st)
        secret = st["secret"]
        shown = st.setdefault("absent", [])
        candidates = [v for v in VOWELS if v not in secret and v not in shown]
        notice = None
        if not candidates:
            notice = "Boshqa yo'q unli qolmadi."
        elif wallet["vowel"] <= 0:
            notice = "Yo'q unli hamyoningiz bo'sh. Har g'alabada +1 qo'shiladi."
        else:
            shown.append(random.choice(candidates))
            wallet["vowel"] -= 1
        await self._play(update, context, notice)

    # ---------- BaseGame interfeysi ----------

    async def on_open(self, update, context) -> None:
        await self._back(update, context)

    async def on_callback(self, update, context, action: str) -> None:
        st = self._st(context)

        if action in ("hint", "letter", "vowel"):
            if not st.get("secret"):  # eskirgan tugma: o'yin allaqachon tugagan
                await self._home(update, context)
                return
            if action == "hint":
                await self._use_hint(update, context)
            elif action == "letter":
                await self._use_letter(update, context)
            else:
                await self._use_vowel(update, context)
        elif action == "home":
            await self._home(update, context)
        elif action == "back":
            await self._back(update, context)
        elif action == "new":
            if not st.get("secret"):
                self._start_new(st)
            await self._play(update, context)
        elif action == "rules":
            rows = [[button("⬅️ Orqaga", f"g:{self.id}:back"), home_button()]]
            text = texts.rules(WORD_LENGTH, MAX_ATTEMPTS, START_WALLET, MAX_WALLET, MAX_LETTER_REVEALS)
            await show(update, context, text, rows)
        elif action == "stats":
            rows = [[button("⬅️ Orqaga", f"g:{self.id}:back"), home_button()]]
            text = texts.stats(st.get("wins", 0), st.get("losses", 0), st.get("best"), self._wallet(st))
            await show(update, context, text, rows)
        elif action == "giveup":
            if not st.get("secret"):
                await self._home(update, context)
                return
            rows = [
                [button("✅ Ha, taslim bo'laman", f"g:{self.id}:giveup_yes")],
                [button("↩️ Yo'q, davom etaman", f"g:{self.id}:back")],
            ]
            await show(update, context, texts.confirm_giveup(), rows)
        elif action == "giveup_yes":
            if st.get("secret"):
                await self._finish(update, context, won=False, gave_up=True)
            else:
                await self._home(update, context)
        else:
            await self._back(update, context)

    async def on_text(self, update, context) -> None:
        await delete_user_message(update)  # yozilgan so'z tarixda ko'rinadi, chat toza turadi
        st = self._st(context)
        secret = st.get("secret")
        if not secret:
            await self._home(update, context, notice="Avval ▶️ Yangi o'yin tugmasini bosing.")
            return

        res = uzbek.parse_word(update.message.text or "", WORD_LENGTH)
        if res.error:
            await self._play(update, context, notice=res.error)
            return
        if res.ambiguous:
            options = "\n".join("• " + uzbek.show_word(r, spaced=True) for r in res.ambiguous)
            notice = (
                "Bu so'zni ikki xil o'qish mumkin:\n"
                f"{options}\n"
                "Alohida harflarning orasiga chiziqcha qo'ying, masalan: s-hanga (s va h alohida)."
            )
            await self._play(update, context, notice=notice)
            return

        guess = res.tokens
        history = st.setdefault("history", [])
        if any(h["t"] == guess for h in history):
            await self._play(update, context, notice="Bu so'zni allaqachon yozgansiz.")
            return

        green, yellow, red = score(secret, guess)
        history.append({"t": guess, "g": green, "y": yellow, "r": red})

        if guess == secret:
            await self._finish(update, context, won=True)
        elif len(history) >= MAX_ATTEMPTS:
            await self._finish(update, context, won=False)
        else:
            await self._play(update, context)


GAME = Word500()
