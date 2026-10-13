"""
Uzbek text normalization.

Uzbek chats mix Latin and Cyrillic (often inside one word), write o'/g' with
half a dozen different apostrophes, and evade filters with digits, stretched
letters and letter-by-letter spelling. Everything here reduces those variants
to one comparable form while remembering where every output character came
from, so a detection can still be pointed at the original text.

Two levels:
- ``to_latin`` - readable Uzbek Latin (good for ML features and logs)
- ``fold``     - lossy matching form: o'->o, g'->g, x->h, no apostrophes,
                 stretched letters collapsed. Only for comparisons.
"""
from __future__ import annotations

import re
import unicodedata
from itertools import groupby
from typing import NamedTuple

# every apostrophe-like mark people use in o'/g'/sun'iy
APOSTROPHES = "'`´ʻʼʹʽˈ‘’‛′"

_CYR_TO_LAT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "ё": "yo",
    "ж": "j", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "x", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sh",
    "ъ": "'", "ы": "i", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    # Uzbek-specific
    "ў": "o'", "қ": "q", "ғ": "g'", "ҳ": "h",
    # lookalikes from neighbouring alphabets (kk/ky/uk keyboards)
    "і": "i", "ї": "yi", "є": "ye", "ң": "ng", "ү": "u", "ұ": "u",
    "ө": "o", "ә": "a", "һ": "h", "ј": "j",
}

# Turkish/Azeri-style Latin that Uzbek users sometimes type
_LAT_VARIANTS = {
    "ğ": "g'", "ş": "sh", "ç": "ch", "ö": "o'", "ő": "o'", "õ": "o'",
    "ô": "o'", "ü": "u", "ı": "i", "ñ": "ng", "ә": "a",
}

_VOWELS = set("aeiouаеёиоуэюяўы")

# digit/symbol substitutions used to dodge filters ("s1kay" -> "sikay")
_LEET = {
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t",
    "@": "a", "$": "s",
}

# q stays q: "siqmoq" (squeeze) vs "sikmoq" is a real distinction
_FOLD = {"x": "h", "w": "v"}

_TOKEN_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


class MappedText(NamedTuple):
    """Normalized text plus, for each character, its index in the source."""

    text: str
    offsets: tuple[int, ...]

    def source_span(self, start: int, end: int) -> tuple[int, int]:
        return self.offsets[start], self.offsets[end - 1] + 1


def _clean_chars(text: str) -> list[tuple[str, int]]:
    """NFKC + casefold + strip invisible chars, keeping source indexes."""
    out: list[tuple[str, int]] = []
    for index, char in enumerate(text):
        normalized = unicodedata.normalize("NFKC", char).casefold()
        for item in normalized:
            if unicodedata.category(item) == "Cf":
                continue
            if item in APOSTROPHES:
                item = "'"
            out.append((item, index))
    return out


def _transliterate(chars: list[tuple[str, int]]) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    prev = ""
    for char, index in chars:
        if char == "е":
            # word-initial / after a vowel "е" is read "ye" (ер -> yer)
            latin = "ye" if (not prev or not prev.isalpha() or prev in _VOWELS
                             or prev in "ъь") else "e"
        else:
            latin = _CYR_TO_LAT.get(char) or _LAT_VARIANTS.get(char) or char
        prev = char
        out.extend((item, index) for item in latin)
    return out


def _apply_leet(chars: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """
    Undo digit/symbol substitutions inside words only: "s1kay", "p1zd4",
    "$uka". A digit is replaced only right after a letter and not next to
    another digit, so "23-bandiga", "5ta", "100som" stay numbers.
    """
    out = list(chars)
    n = len(chars)
    for pos, (char, index) in enumerate(chars):
        if char not in _LEET:
            continue
        prev = chars[pos - 1][0] if pos > 0 else ""
        nxt = chars[pos + 1][0] if pos + 1 < n else ""
        if char.isdigit():
            ok = prev.isalpha() and not nxt.isdigit()
        else:
            ok = nxt.isalpha() or prev.isalpha()
        if ok:
            out[pos] = (_LEET[char], index)
    return out


def _to_latin_chars(text: str) -> list[tuple[str, int]]:
    return _transliterate(_clean_chars(text))


def _join(chars: list[tuple[str, int]]) -> MappedText:
    return MappedText("".join(c for c, _ in chars), tuple(i for _, i in chars))


def to_latin(text: str) -> str:
    """Readable lowercase Uzbek Latin: both scripts and all apostrophes unified."""
    return _join(_to_latin_chars(text)).text


def fold_mapped(text: str) -> MappedText:
    """Lossy matching form with a source index for every character."""
    chars = _apply_leet(_to_latin_chars(text))
    out: list[tuple[str, int]] = []
    for char, index in chars:
        if char == "'":
            continue  # o'->o, g'->g, sun'iy->suniy
        out.append((_FOLD.get(char, char), index))
    # collapse stretched letters: "jalaaaab" -> "jalab" (3+ only, so real
    # double letters like "sikka", "jallab" keep their shape)
    collapsed: list[tuple[str, int]] = []
    for char, group in groupby(out, key=lambda item: item[0]):
        items = list(group)
        collapsed.extend(items[:1] if len(items) >= 3 and char.isalpha() else items)
    return _join(collapsed)


def fold(text: str) -> str:
    return fold_mapped(text).text


class Candidate(NamedTuple):
    word: str
    start: int  # span in the folded text
    end: int


def candidates(folded: str) -> list[Candidate]:
    """
    Words to check, including ones rebuilt from evasion tricks:
    - plain tokens:                "salom jalab"   -> salom, jalab
    - punctuation inside a chunk:  "j.a.l.a.b", "si*kay" -> jalab, sikay
    - spaced letters:              "s i k a y", "ja l a b" -> sikay, jalab
    """
    found: dict[tuple[str, int], Candidate] = {}

    def add(word: str, start: int, end: int) -> None:
        if word:
            found.setdefault((word, start), Candidate(word, start, end))

    tokens = [(m.group(), m.start(), m.end()) for m in _TOKEN_RE.finditer(folded)]
    for word, start, end in tokens:
        add(word, start, end)

    for chunk in re.finditer(r"\S+", folded):
        letters = "".join(_TOKEN_RE.findall(chunk.group()))
        if letters:
            add(letters, chunk.start(), chunk.end())

    # runs of short fragments separated by spaces/punctuation
    run: list[tuple[str, int, int]] = []

    def flush() -> None:
        # every suffix of the run, so short real words in front of the
        # spelled-out one ("va s i k a y") don't hide it from prefix matching
        for i in range(len(run) - 1):
            tail = run[i:]
            if any(len(w) == 1 for w, _, _ in tail):
                joined = "".join(w for w, _, _ in tail)
                if len(joined) >= 3:
                    add(joined, tail[0][1], tail[-1][2])
        run.clear()

    for word, start, end in tokens:
        if len(word) <= 2:
            run.append((word, start, end))
        else:
            flush()
    flush()

    return list(found.values())
