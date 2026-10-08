"""
O'zbek lotin alifbosi bilan ishlash (hamma so'z o'yinlari uchun umumiy).

O'zbek alifbosida bir nechta belgidan iborat harflar bor: o'  g'  sh  ch  ng
Bu fayl so'zni "belgilar"ga emas, aynan HARFlarga ajratadi.

Qoidalar:
1. o' va g' har doim bitta harf (apostrof harfning bir qismi).
2. ch har doim bitta harf (alifboda alohida "c" yo'q).
3. sh va ng noaniq: ular bitta harf bo'lishi ham, ikki alohida harf
   (s+h, n+g) bo'lishi ham mumkin (masalan: "shahar" va "ishor", "dengiz" va "tanga").
   Shuning uchun maqsad uzunlikka qaraymiz: so'z aynan `length` harfga
   tushishi uchun nechta sh/ng ni birlashtirish kerak bo'lsa, shuncha birlashtiramiz.
4. Qo'lda ko'rsatish:
     [sh]  - qavs ichidagi harflar albatta bitta harf (boshqa sh/ng lar birlashtirilmaydi)
     s-h   - chiziqcha: shu ikki harf alohida harf (birlashtirilmaydi)
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from pathlib import Path

# Turli apostroflar (telefon klaviaturalari har xil belgi yozadi)
_APOSTROPHES = "\u02bb\u02bc\u2018\u2019`\u00b4\u2032\u02b9\u02bd"
LETTERS = set("abcdefghijklmnopqrstuvwxyz")
_PAIRS = {("s", "h"), ("n", "g")}
_MAX_RAW = 24


@dataclass
class _Tok:
    text: str
    barrier: bool = False  # oldidagi harf bilan birlashtirish taqiqlangan (chiziqcha)


@dataclass
class ParseResult:
    tokens: list[str] | None = None          # aniq natija: harflar ro'yxati
    error: str | None = None                 # xato matni
    ambiguous: list[list[str]] | None = None  # bir nechta mumkin bo'lgan o'qilish

    @property
    def ok(self) -> bool:
        return self.tokens is not None


def normalize(text: str) -> str:
    """Kichik harfga o'tkazadi va barcha apostroflarni bitta turga keltiradi."""
    text = text.strip().lower()
    for a in _APOSTROPHES:
        text = text.replace(a, "'")
    return text


def show_word(tokens: list[str], spaced: bool = False) -> str:
    """Harflar ro'yxatini katta harfda ko'rsatadi. spaced=True: harflar orasida bo'sh joy."""
    parts = [t.upper() for t in tokens]
    return (" " if spaced else "").join(parts)


def _count_error(base: int, length: int) -> str:
    return f"So'z {length} harfli bo'lishi kerak, siz {base} harfli so'z yozdingiz."


def _tokenize(text: str):
    """Matnni dastlabki harflarga ajratadi (o', g', ch, [..] majburiy birlashadi).
    Qaytaradi: (tokenlar, qavs_ishlatildimi, xato)."""
    toks: list[_Tok] = []
    explicit = False
    barrier = False
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "-":
            barrier = True
            i += 1
            continue
        if ch == "[":
            j = text.find("]", i + 1)
            if j == -1:
                return None, False, "Qavs yopilmagan. Masalan: [sh]"
            inner = text[i + 1:j]
            if len(inner) < 2 or not all(c in LETTERS for c in inner):
                return None, False, "Qavs ichida kamida 2 ta lotin harfi bo'lishi kerak. Masalan: [sh]"
            toks.append(_Tok(inner, barrier))
            barrier = False
            explicit = True
            i = j + 1
            continue
        if ch == "]":
            return None, False, "Qavs noto'g'ri qo'yilgan."
        if ch in LETTERS:
            nxt = text[i + 1] if i + 1 < n else ""
            if ch in "og" and nxt == "'":
                toks.append(_Tok(ch + "'", barrier))
                i += 2
            elif ch == "c" and nxt == "h":
                toks.append(_Tok("ch", barrier))
                i += 2
            else:
                toks.append(_Tok(ch, barrier))
                i += 1
            barrier = False
            continue
        if ch == "'":
            return None, False, "Tutuq belgisi (') harf emas. Apostrof faqat o' va g' harflarida bo'ladi."
        return None, False, f"Faqat lotin harflari ishlatilsin: '{ch}' mumkin emas."
    return toks, explicit, None


def parse_word(raw: str, length: int, allow_merge: bool = True) -> ParseResult:
    """
    So'zni `length` ta harfga ajratadi.

    allow_merge=False: sh/ng ni birlashtirish taqiqlangan (words.txt da "*" belgisiz so'zlar).
    allow_merge=True : kerak bo'lsa sh/ng birlashtiriladi (o'yinchi taxmini, "*" li so'zlar).
    """
    text = normalize(raw)
    if not text:
        return ParseResult(error="So'z bo'sh.")
    if len(text) > _MAX_RAW:
        return ParseResult(error="So'z juda uzun.")

    toks, explicit, err = _tokenize(text)
    if err:
        return ParseResult(error=err)

    # Qavs ishlatilgan bo'lsa - hammasi aniq, taxmin qilinmaydi
    if explicit:
        words = [t.text for t in toks]
        if len(words) != length:
            return ParseResult(error=_count_error(len(words), length))
        return ParseResult(tokens=words)

    base = len(toks)
    need = base - length  # nechta sh/ng ni birlashtirish kerak
    if need < 0:
        return ParseResult(error=_count_error(base, length))
    if need == 0:
        return ParseResult(tokens=[t.text for t in toks])

    if not allow_merge:
        return ParseResult(
            error=(
                f"belgisiz so'z {base} harfdan iborat ({length} bo'lishi kerak). "
                "Agar unda sh yoki ng birlashgan harf bo'lsa, so'z boshiga * qo'ying."
            )
        )

    cands = [
        i for i in range(base - 1)
        if (toks[i].text, toks[i + 1].text) in _PAIRS and not toks[i + 1].barrier
    ]
    if need > len(cands):
        return ParseResult(error=f"So'z {length} harfdan uzun.")

    readings: list[list[str]] = []
    for combo in itertools.combinations(cands, need):
        merged = set(combo)
        out: list[str] = []
        i = 0
        while i < base:
            if i in merged:
                out.append(toks[i].text + toks[i + 1].text)
                i += 2
            else:
                out.append(toks[i].text)
                i += 1
        readings.append(out)

    if len(readings) == 1:
        return ParseResult(tokens=readings[0])
    return ParseResult(ambiguous=readings)


def load_word_entries(path: str | Path, length: int) -> tuple[list[tuple[list[str], list[str]]], list[str]]:
    """
    words.txt ni o'qiydi. Har qatorda bitta so'z, undan keyin ixtiyoriy maslahatlar ("|" bilan):

        baliq | suvda yashaydi | tangachasi bor | qovurib yeyiladi
        *shahar | ko'p odam yashaydi
        bahor

      - belgisiz so'z aynan `length` harf bo'lishi kerak
      - "*" bilan boshlangan so'zda sh/ng birlashgan harf bo'lishi mumkin
      - "|" dan keyingi har bir bo'lak - bitta maslahat (maslahatsiz so'z ham mumkin)
      - "#" bilan boshlangan qator izoh

    Qaytaradi: ([(harflar, maslahatlar), ...], muammolar ro'yxati).
    Muammoli qatorlar tashlab yuboriladi, lekin muammolar ro'yxatida qator raqami bilan ko'rsatiladi.
    """
    path = Path(path)
    if not path.exists():
        return [], [f"{path.name} fayli topilmadi"]

    entries: list[tuple[list[str], list[str]]] = []
    problems: list[str] = []
    seen: set[tuple[str, ...]] = set()

    with path.open(encoding="utf-8-sig") as f:  # utf-8-sig: Notepad qo'shgan BOM ni olib tashlaydi
        for lineno, line in enumerate(f, 1):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = [p.strip() for p in s.split("|")]
            word_part = parts[0]
            hints = [p for p in parts[1:] if p]
            star = word_part.startswith("*")
            body = word_part.lstrip("*").strip()
            res = parse_word(body, length, allow_merge=star)
            if res.error:
                problems.append(f'{lineno}-qator "{s}": {res.error}')
                continue
            if res.ambiguous:
                options = " yoki ".join(show_word(r, spaced=True) for r in res.ambiguous)
                problems.append(
                    f'{lineno}-qator "{s}": ikki xil o\'qilishi mumkin ({options}). '
                    "Birlashgan harfni qavsga oling, masalan: *[sh]anga"
                )
                continue
            key = tuple(res.tokens)
            if key in seen:
                continue
            seen.add(key)
            entries.append((list(res.tokens), hints))

    return entries, problems


def load_word_list(path: str | Path, length: int) -> tuple[list[list[str]], list[str]]:
    """Faqat so'zlarni (maslahatsiz) qaytaradi. Maslahatlar kerak bo'lsa load_word_entries ni ishlating."""
    entries, problems = load_word_entries(path, length)
    return [tokens for tokens, _ in entries], problems
