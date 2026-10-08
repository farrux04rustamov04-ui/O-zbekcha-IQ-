"""
Botni ishga tushirish:   python bot.py

Token bot.py bilan bir papkadagi token.txt faylidan o'qiladi
(ichida faqat BotFather bergan token bo'lsin).
Fayl bo'lmasa, BOT_TOKEN muhit o'zgaruvchisidan olinadi.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from telegram.ext import Application, PicklePersistence  # noqa: E402

from core import menu, registry  # noqa: E402

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("bot")


def read_token() -> str:
    token = ""
    path = ROOT / "token.txt"
    if path.exists():
        lines = path.read_text(encoding="utf-8-sig").strip().splitlines()
        token = lines[0].strip() if lines else ""
    if not token:
        token = os.environ.get("BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "Token topilmadi. Bot bilan bir papkada token.txt fayl yarating "
            "va ichiga faqat BotFather bergan tokenni yozing."
        )
    return token


def main() -> None:
    token = read_token()

    registry.load_sections()
    registry.load_games()

    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    # Foydalanuvchilar ma'lumoti (statistika, joriy o'yin) bot o'chib yonganda ham saqlanadi
    persistence = PicklePersistence(filepath=str(data_dir / "bot_data.pkl"), update_interval=10)

    app = Application.builder().token(token).persistence(persistence).build()
    menu.register(app)

    log.info("Bot ishga tushdi. To'xtatish: Ctrl+C")
    app.run_polling()


if __name__ == "__main__":
    main()
