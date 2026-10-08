"""So'zni top: bot xabarlari. Matnlar HTML formatida (<b>, <i>, <code>)."""

from __future__ import annotations

import html

# O'yin nomi faqat shu yerda o'zgartiriladi (menyu tugmasi va barcha sarlavhalar shundan olinadi)
GAME_NAME = "So'zni top"
TITLE = f"🔤 <b>{GAME_NAME}</b>"


def _esc(s: str) -> str:
    return html.escape(s, quote=False)


def _notice(notice: str | None) -> str:
    return f"⚠️ {_esc(notice)}\n\n" if notice else ""


def _stats_line(wins: int, losses: int) -> str:
    return f"📊 G'alaba: {wins} | Mag'lubiyat: {losses}"


def _wallet_line(wallet: dict) -> str:
    return f"🎁 Yordam: 💡 {wallet['hint']} · 🔤 {wallet['letter']} · 🚫 {wallet['vowel']}"


def rules(length: int, attempts: int, start: int, cap: int, max_letters: int) -> str:
    return (
        f"📖 <b>{GAME_NAME} qoidalari</b>\n\n"
        f"Men {length} harfli yashirin so'z o'ylayman. Sizda {attempts} ta urinish bor.\n\n"
        "Har bir taxminingizdan keyin 3 ta son beraman:\n"
        "🟩 — harf so'zda bor va joyi to'g'ri\n"
        "🟨 — harf so'zda bor, lekin joyi noto'g'ri\n"
        "🟥 — harf so'zda yo'q\n\n"
        "Qaysi harflar to'g'ri ekanini aytmayman, buni o'zingiz topasiz! 🧠\n\n"
        "🆘 <b>Yordamlar</b>\n"
        f"Har biridan {start} tadan beriladi. Har g'alabada har biriga +1 qo'shiladi "
        f"(ko'pi bilan {cap} ta). Xohlasangiz bitta o'yinda hammasini ishlating, "
        "xohlasangiz tejab, ko'proq o'yin o'ynang.\n"
        "💡 <b>Maslahat</b> — so'z haqida ishora. Har bosganingizda keyingisi ochiladi.\n"
        f"🔤 <b>Harf ochish</b> — bitta harf o'z joyi bilan ochiladi (bir o'yinda {max_letters} tagacha).\n"
        "🚫 <b>Yo'q unli</b> — so'zda yo'q unlilardan biri ko'rsatiladi (a, e, i, o, o', u).\n"
        "Ishlatilmagan yoki foydasiz bosilgan yordam hamyondan ayirilmaydi.\n\n"
        "ℹ️ <b>O'zbek harflari:</b> o', g', sh, ch, ng bitta harf hisoblanadi. "
        "Masalan, SHAHAR 5 harfli so'z (sh-a-h-a-r).\n\n"
        "Agar so'zni ikki xil o'qish mumkin bo'lsa (masalan shanga), "
        "alohida harflarning orasiga chiziqcha qo'ying: <code>s-hanga</code> "
        "(s va h alohida harf)."
    )


def home(length: int, attempts: int, wins: int, losses: int, wallet: dict,
         notice: str | None = None) -> str:
    return (
        f"{TITLE}\n\n{_notice(notice)}"
        f"{length} harfli yashirin so'zni {attempts} ta urinishda toping!\n\n"
        f"{_stats_line(wins, losses)}\n"
        f"🏅 Daraja: {wins}\n"
        f"{_wallet_line(wallet)}"
    )


def hints_block(shown: list[str], total: int) -> str:
    lines = [f"💡 <b>Maslahatlar ({len(shown)}/{total}):</b>"]
    lines += [f"{i}) {_esc(h)}" for i, h in enumerate(shown, 1)]
    return "\n".join(lines)


def letters_line(cells: list[str]) -> str:
    return "🔤 <b>" + " ".join(_esc(c) for c in cells) + "</b>"


def absent_line(vowels: list[str]) -> str:
    return "🚫 So'zda yo'q unlilar: <b>" + ", ".join(_esc(v) for v in vowels) + "</b>"


def play(helps: str, lines: list[str], left: int, length: int, notice: str | None = None) -> str:
    body = "\n".join(lines) if lines else "<i>Hali taxmin yo'q.</i>"
    helps_part = f"{helps}\n\n" if helps else ""
    return (
        f"{TITLE}\n\n{_notice(notice)}{helps_part}{body}\n\n"
        f"✍️ {length} harfli so'z yozing. Qolgan urinishlar: <b>{left}</b>"
    )


def history_line(i: int, word: str, green: int, yellow: int, red: int) -> str:
    return f"{i}.  🟩{green}  🟨{yellow}  🟥{red}   <b>{_esc(word)}</b>"


def finished(lines: list[str], secret: str, won: bool, gave_up: bool, attempts: int,
             wins: int, losses: int, bonus: bool = False) -> str:
    if won:
        head = f"🎉 <b>Tabriklayman!</b> {attempts}-urinishda topdingiz: <b>{_esc(secret)}</b>"
        extra = f"\n🏅 Daraja: {wins}"
        if bonus:
            extra += "\n🎁 Har bir yordamga +1 qo'shildi."
    elif gave_up:
        head = f"🏳️ Taslim bo'ldingiz. So'z: <b>{_esc(secret)}</b>"
        extra = ""
    else:
        head = f"😔 Urinishlar tugadi. So'z: <b>{_esc(secret)}</b>"
        extra = ""
    body = ("\n".join(lines) + "\n\n") if lines else ""
    return f"{TITLE}\n\n{body}{head}\n\n{_stats_line(wins, losses)}{extra}"


def confirm_giveup() -> str:
    return f"{TITLE}\n\n🏳️ Rostdan ham taslim bo'lasizmi? Bu mag'lubiyat hisoblanadi."


def stats(wins: int, losses: int, best: int | None, wallet: dict) -> str:
    total = wins + losses
    rate = round(100 * wins / total) if total else 0
    best_text = f"{best}-urinishda" if best else "—"
    return (
        "📊 <b>Statistika</b>\n\n"
        f"O'yinlar: {total}\n"
        f"G'alaba: {wins}\n"
        f"Mag'lubiyat: {losses}\n"
        f"G'alaba foizi: {rate}%\n"
        f"Eng tez topilgan: {best_text}\n"
        f"🏅 Daraja: {wins}\n\n"
        "🎁 <b>Yordam hamyoni</b>\n"
        f"💡 Maslahat: {wallet['hint']}\n"
        f"🔤 Harf ochish: {wallet['letter']}\n"
        f"🚫 Yo'q unli: {wallet['vowel']}"
    )
