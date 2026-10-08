"""
Foydalanuvchi ma'lumotlari.

Hammasi context.user_data ichida turadi va bot qayta ishga tushganda ham saqlanadi
(data/bot_data.pkl fayli). Har bir o'yin o'z nomi ostidagi alohida lug'atdan
foydalanadi, shuning uchun o'yinlar bir-birining ma'lumotini aralashtirmaydi.

user_data tuzilmasi:
    "mode"   - hozir qaysi o'yinda ekani (o'yin id si yoki None)
    "screen" - botning oxirgi menyu xabari [chat_id, message_id]
    "games"  - {o'yin_id: {...o'yinning o'z ma'lumotlari...}}
"""

from __future__ import annotations


def game_store(user_data: dict, game_id: str) -> dict:
    """Shu o'yinning shu foydalanuvchiga tegishli ma'lumotlar lug'ati."""
    return user_data.setdefault("games", {}).setdefault(game_id, {})
