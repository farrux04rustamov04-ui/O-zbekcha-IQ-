"""
"O'yinlar" bo'limi: games/ papkasidagi barcha o'yinlarni ro'yxat qilib ko'rsatadi.
Yangi o'yin qo'shganingizda bu faylga tegmaysiz.
"""

from __future__ import annotations

from core import registry, ui
from core.base import Section


class GamesSection(Section):
    id = "games"
    title = "🎮 O'yinlar"
    order = 10

    async def show(self, update, context):
        games = list(registry.GAMES.values())
        if games:
            text = "🎮 <b>O'yinlar</b>\n\nQaysi o'yinni o'ynaymiz?"
            rows = [[ui.button(g.title, f"g:{g.id}:open")] for g in games]
        else:
            text = "🎮 <b>O'yinlar</b>\n\nHozircha o'yinlar yo'q."
            rows = []
        rows.append([ui.home_button()])
        await ui.show(update, context, text, rows)


SECTION = GamesSection()
