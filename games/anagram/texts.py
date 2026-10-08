"""Anagramma: bot xabarlari."""

from __future__ import annotations
import html

TITLE = "🔤 <b>Anagramma</b>"

def _esc(s: str) -> str:
    return html.escape(s, quote=False)

def _notice(notice: str | None) -> str:
    return f"⚠️ {_esc(notice)}\n\n" if notice else ""

def _stats_line(wins: int, losses: int) -> str:
    return f"📊 G'alaba: {wins} | Mag'lubiyat: {losses}"

def rules() -> str:
    return (
        "📖 <b>Anagramma o'yini qoidalari</b>\n\n"
        "Men sizga harflari aralashtirib yuborilgan so'zni yuboraman. "
        "Sizning vazifangiz — harflarni to'g'ri tartibda yig'ib, asl so'zni topish.\n\n"
        "Masalan: <b>r-h-a-a-b</b> ➡️ <b>Bahor</b> 🧠"
    )

def home(wins: int, losses: int, notice: str | None = None) -> str:
    return (
        f"{TITLE}\n\n{_notice(notice)}"
        "Aralashib ketgan harflardan to'g'ri so'z tuzing!\n\n"
        f"{_stats_line(wins, losses)}"
    )

def play(scrambled: str, score_count: int, notice: str | None = None) -> str:
    return (
        f"{TITLE}\n\n"
        f"{_notice(notice)}"
        f"Aralash so'z: 🔠 <code>{_esc(scrambled)}</code>\n\n"
        "Ushbu harflardan qaysi so'z chiqqanini yozing:\n\n"
        f"🏆 Topilgan so'zlar: <b>{score_count}</b>"
    )

def stats(wins: int, losses: int) -> str:
    total = wins + losses
    rate = round(100 * wins / total) if total else 0
    return (
        "📊 <b>Statistika</b>\n\n"
        f"O'yinlar (topilgan so'zlar): {wins}\n"
        f"Xatolar (o'tkazib yuborilgan): {losses}\n"
        f"Muvaffaqiyat: {rate}%"
    )