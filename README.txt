BOT TUZILMASI
=============
bot.py               - ishga tushirish (python bot.py)
token.txt            - SIZ yaratasiz: ichida faqat BotFather tokeni
core/                - yadro: menyu, yo'naltirish, saqlash (o'yinlarni bilmaydi)
shared/uzbek.py      - o'zbek harflarini ajratish (hamma so'z o'yinlari uchun umumiy)
sections/            - bosh menyu bo'limlari (hozir: games.py - "O'yinlar")
games/word500/       - Word 500: game.py (mantiq), texts.py (matnlar), words.txt (so'zlar)
data/                - foydalanuvchi statistikasi (avtomatik yaratiladi, o'chirmang)

YANGI O'YIN QO'SHISH
====================
1. games/ ichida yangi papka oching, masalan games/anagram/
2. Ichiga __init__.py va game.py yozing
3. game.py ichida core.base.BaseGame dan meros oluvchi sinf yozing va oxirida GAME = Sinf()
4. Botni qayta ishga tushiring - tugma "O'yinlar" ro'yxatida o'zi paydo bo'ladi.
(games/word500/game.py ni namuna qilib oling)

YANGI BO'LIM QO'SHISH (bosh menyuga)
====================================
sections/ ichida yangi .py fayl yozing: core.base.Section dan meros oluvchi sinf
va oxirida SECTION = Sinf(). Tugma bosh menyuda o'zi paydo bo'ladi.

WORDS.TXT QOIDALARI
===================
bahor, ishor, tanga     - oddiy so'z, aynan 5 belgi
o'rdak, tog'am, chiroq  - o' g' ch uchun hech narsa kerak emas
*shahar, *eshshak       - sh yoki ng birlashgan harf bo'lsa, boshiga * qo'ying
*[sh]anga               - kamdan-kam: birlashganini qavsga oling
# izoh                  - izoh qatori
Xato qatorlar bot ishga tushganda konsolda qator raqami bilan ko'rsatiladi.
