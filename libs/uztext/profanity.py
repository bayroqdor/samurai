"""
Uzbek profanity detector.

Uzbek is agglutinative: one obscene root shows up with dozens of suffixes
("sikay", "sikaman", "sikib", "sikvoraman"...). Instead of listing word forms,
each entry is a regex matched at the *start* of a folded word (see
``normalize.fold``), so suffixes are covered for free and a few negative
lookaheads keep innocent words ("sikl", "sikka", "ko'taring") clean.

Patterns are written against the folded form: no apostrophes, x->h.
q is NOT folded into k: "siqmoq" (to squeeze) must not collide with "sikmoq",
so patterns spell out [kq] where both occur.

The list also carries Russian mat in Latin transliteration ("nahuy", "blyat"),
which is very common in Uzbek chats and is invisible to the Cyrillic-only
Russian filter.

The lexicon is a starting point; native speakers should extend it through
``[profanity] blocklist_uz`` in config.toml rather than editing code.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from .normalize import MappedText, candidates, fold, fold_mapped

# (pattern, label). Matched with re.match against a single folded word.
_UZ_ROOTS: tuple[tuple[str, str], ...] = (
    # sikmoq and derivatives. Excluded: sikl (cycle), sikka (coin), sikh,
    # Sikandar (name), sikada (cicada), and sikil-, which is how "siqilmoq"
    # (to feel down) looks when typed on a Russian keyboard without "қ"
    (r"sik(?!l|k|h|il|and|ad)", "sik*"),
    (r"siktir", "siktir"),
    # shortened chat spelling of the same verb; ski/skidka/skype/skeyt stay clean
    (r"sk(?:ay(?!p)|ey(?!t)|iy|aman|asan|ib\b|ilgan|vor|aver)", "sk*"),
    # qo'toq / qo'taq / кутак
    (r"[kq][ou]t[ao][kgq]", "qo'toq"),
    # ko't (ass) - only possessive forms, "ko'tarmoq" (to lift) is everyday
    (r"kot(?:ing|imga|imni|imdan|ini|inga|ingga|ingni|ingdan)", "ko't*"),
    (r"jall?a(?:b|p(?!en))", "jalab"),
    (r"[kq]anj[iy][kgq]", "qanjiq"),
    (r"[kq]ahba", "qahba"),
    (r"fohish", "fohisha"),
    (r"d[ao]lb[ao]y?[oe][bp]", "dalbayob"),
    # am (vulgar) - only unambiguous forms; "Amin", "amaki" stay clean
    (r"am(?:ingga|ingni|ingdan|jalab)", "am*"),
    (r"p[ie]d(?:or|ar|[ae]ras|rila)|pidr", "pidor"),
    # Russian mat, Latin spelling (x folds to h)
    (r"(?:na|po|ni|za|o)?huy", "huy"),
    (r"(?:na|po)hui", "huy"),
    (r"(?:ras|za|o)?pizd", "pizd*"),
    (r"bly(?:at|ad|a\b|ya)", "blyat"),
    (r"y?eb(?:at|an|al|lan|ash|nut|uch|anu)", "ebat"),
    (r"(?:za|vy|ras|raz|pro|ot|po|na|do)y?eb(?:a|an|al|u|i|n)", "ebat"),
    (r"u[ey]?[eo]bok|uyob", "uebok"),
    (r"suk(?:a|i|ami|in)\b", "suka"),
    (r"mud(?:ak|ila|ilo|oz)", "mudak"),
    (r"zalup", "zalupa"),
    (r"shl[yi]u[hk]|shluh", "shluha"),
    (r"s?hues[oa]s", "huesos"),
    (r"g[ao]nd[o]n", "gandon"),
    (r"ebl[oa]", "ebat"),
    (r"suchk[ai]", "suchka"),
    (r"droch", "drochit"),
    (r"trah(?:at|al|ay|nu)", "trahat"),
    # English swears Uzbek chats borrow (the English filter is skipped for
    # Uzbek text); "fukaro" is fuqaro typed without "қ", "fukusima" a place
    (r"fuck|fuk(?![aeu])", "fuck"),
    (r"motherf|bitch|cunt|whore|slut\b", "en"),
)

_COMPILED = tuple((re.compile(pattern), label) for pattern, label in _UZ_ROOTS)


@dataclass(frozen=True, slots=True)
class UzMatch:
    word: str        # folded word that matched
    label: str       # which root fired
    start: int       # span in the ORIGINAL text
    end: int


def _compile_blocklist(blocklist: Iterable[str]) -> tuple[tuple[re.Pattern, str], ...]:
    compiled = []
    for item in blocklist:
        folded = fold(item).strip()
        if folded:
            compiled.append((re.compile(re.escape(folded)), item))
    return tuple(compiled)


def find(
    text: str,
    *,
    allowlist: Iterable[str] = (),
    blocklist: Iterable[str] = (),
) -> UzMatch | None:
    """First profanity match in ``text`` or None.

    ``allowlist`` - exact words never treated as profanity.
    ``blocklist`` - extra roots, prefix-matched like the built-in ones.
    """
    if not text:
        return None
    mapped: MappedText = fold_mapped(text)
    allowed = {fold(word) for word in allowlist if word}
    rules = _COMPILED + _compile_blocklist(blocklist)

    # shorter / plain candidates first, so the reported span is tight
    for cand in sorted(candidates(mapped.text), key=lambda c: (c.end - c.start, c.start)):
        if cand.word in allowed:
            continue
        for pattern, label in rules:
            if pattern.match(cand.word):
                start, end = mapped.source_span(cand.start, cand.end)
                return UzMatch(cand.word, label, start, end)
    return None
