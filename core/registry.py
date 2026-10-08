"""
games/ va sections/ papkalarini avtomatik topadi.

games/<nom>/game.py ichida  GAME = ...  bo'lsa, o'yin ro'yxatga qo'shiladi.
sections/<nom>.py ichida    SECTION = ... bo'lsa, bo'lim bosh menyuga qo'shiladi.
Biror o'yin yoki bo'lim xato bersa, u o'tkazib yuboriladi, bot to'xtamaydi.
"""

from __future__ import annotations

import importlib
import logging
from pathlib import Path

from .base import BaseGame, Section

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent

GAMES: dict[str, BaseGame] = {}
SECTIONS: dict[str, Section] = {}


def load_games() -> None:
    found: list[BaseGame] = []
    games_dir = ROOT / "games"
    for d in sorted(games_dir.iterdir()):
        if not d.is_dir() or d.name.startswith(("_", ".")):
            continue
        if not (d / "game.py").exists():
            continue
        try:
            module = importlib.import_module(f"games.{d.name}.game")
            game = getattr(module, "GAME", None)
            if not isinstance(game, BaseGame) or not game.id:
                log.warning("games/%s/game.py: GAME topilmadi yoki id bo'sh, o'tkazib yuborildi", d.name)
                continue
            game.on_load()
            found.append(game)
        except Exception:
            log.exception("games/%s yuklanmadi, o'tkazib yuborildi", d.name)

    GAMES.clear()
    for game in sorted(found, key=lambda g: (g.order, g.title)):
        if game.id in GAMES:
            log.warning("Takroriy o'yin id: %s, ikkinchisi o'tkazib yuborildi", game.id)
            continue
        GAMES[game.id] = game
    log.info("Yuklangan o'yinlar: %s", ", ".join(GAMES) or "(yo'q)")


def load_sections() -> None:
    found: list[Section] = []
    for f in sorted((ROOT / "sections").glob("*.py")):
        if f.stem.startswith("_"):
            continue
        try:
            module = importlib.import_module(f"sections.{f.stem}")
            section = getattr(module, "SECTION", None)
            if not isinstance(section, Section) or not section.id:
                log.warning("sections/%s.py: SECTION topilmadi, o'tkazib yuborildi", f.stem)
                continue
            found.append(section)
        except Exception:
            log.exception("sections/%s yuklanmadi, o'tkazib yuborildi", f.stem)

    SECTIONS.clear()
    for section in sorted(found, key=lambda s: (s.order, s.title)):
        SECTIONS[section.id] = section
    log.info("Yuklangan bo'limlar: %s", ", ".join(SECTIONS) or "(yo'q)")
