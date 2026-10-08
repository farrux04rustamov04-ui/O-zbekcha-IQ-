"""Sonni top: bot xabarlari."""

from __future__ import annotations
import html

TITLE = "🔢 <b>Sonni top</b>"

def _esc(s: str) -> str:
    return html.escape(s, quote=False)

def _notice(notice: str | None) -> str:
    return f"⚠️️ {_esc(notice)}\n\n" if notice else ""

def _stats_line(wins: int, losses: int) -> str:
    return f"📊 G'alaba: {wins} | Mag'lubiyat: {losses}"

def rules() -> str:
    return (
        "📖 <b>Sonni top o'yini qoidalari</b>\n\n"
        "Men 1 dan 100 gacha bo'lgan tasodifiy son o'ylayman. Sizning vazifangiz — uni topish.\n\n"
        "Har bir taxminingizdan keyin o'ylangan son siz kiritgan sondan katta yoki kichik ekanligi aytiladi. Omad! 🧠"
    )

def home(wins: int, losses: int, notice: str | None = None) -> str:
    return (
        f"{TITLE}\n\n{_notice(notice)}"
        "1 dan 100 gacha yashirin sonni toping!\n\n"
        f"{_stats_line(wins, losses)}"
    )

def play(attempts: int, last_guess: int | None = None, hint: str | None = None, notice: str | None = None) -> str:
    notice_text = f"⚠️ {_esc(notice)}\n\n" if notice else ""
    hint_text = f"💡 Oxirgi taxmin ({last_guess}): <b>{_esc(hint)}</b>\n\n" if hint and last_guess is not None else ""
    
    return (
        f"{TITLE}\n\n"
        f"{notice_text}"
        f"{hint_text}"
        "1 dan 100 gacha son o'yladim. Taxminingizni yuboring:\n\n"
        f"✍️ Urinishlar soni: <b>{attempts}</b>"
    )

def finished(secret: int, attempts: int, wins: int, losses: int) -> str:
    return (
        f"{TITLE}\n\n"
        f"🎉 <b>Tabriklayman!</b> Siz {attempts} ta urinishda to'g'ri topdingiz! 🏆\n"
        f"O'ylangan son: <b>{secret}</b>\n\n"
        f"{_stats_line(wins, losses)}"
    )

def stats(wins: int, losses: int, best: int | None) -> str:
    total = wins + losses
    rate = round(100 * wins / total) if total else 0
    best_text = f"{best} ta urinishda" if best else "—"
    return (
        "📊 <b>Statistika</b>\n\n"
        f"O'yinlar: {total}\n"
        f"G'alaba: {wins}\n"
        f"Mag'lubiyat: {losses}\n"
        f"G'alaba foizi: {rate}%\n"
        f"Eng kam urinish: {best_text}"
    )