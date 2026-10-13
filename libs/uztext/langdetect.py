"""
Cheap "is this Uzbek?" heuristic.

Used to route messages: Russian/English profanity regexes are tuned for those
languages and misfire badly on Uzbek ("Jizzax", "bo'lgandan", "мудофаа"), and
the Russian spam model flags a large share of ordinary Uzbek chat as spam.

Signals, all computed on ``to_latin`` text so both scripts count the same:
- Uzbek-only letters (ў қ ғ ҳ) and Latin o'/g' digraphs
- frequent Uzbek words
- Uzbek suffixes on otherwise unknown words
against Russian/English function words and Russian-only letters (ы, щ).
"""
from __future__ import annotations

import re
from typing import NamedTuple

from .normalize import APOSTROPHES, to_latin

_UZ_CYR_LETTERS = set("ўқғҳЎҚҒҲ")
_RU_ONLY_LETTERS = set("ыщЫЩ")
_UZ_DIGRAPH_RE = re.compile(r"[og]['" + re.escape(APOSTROPHES) + r"](?=[a-z]|\b)")
_WORD_RE = re.compile(r"[a-z']+")

# apostrophes removed, as produced by _words()
_UZ_WORDS = frozenset("""
va bilan uchun emas ham nima nega nimaga qanday qachon qayerda qayerga qayer
kerak kerakmi bor yoq yoqmi sen biz siz ular bu shu ana mana endi hozir juda
yaxshi yahshi rahmat raxmat salom assalomu assalom alaykum aleykum aka opa uka
boladi bolsa bolib boldi bolgan qiling qilib qildi qilish qilaman edi ekan deb
keyin lekin ammo chunki agar hamma bugun ertaga kecha iltimos xop hop mumkin
qaysi menga senga sizga bizga unga meni seni sizni bizni uni mening sening
sizning bizning uning ozim ozing ozi bitta yana faqat kabi haqida orqali oldin
song birga hech nimadir bilmayman bilasizmi ayting yozing oling beraman beradi
keldi ketdi qoldi ishlaydi narxi narx sotiladi sotaman guruh guruhga kanalga
yoki balki albatta qani nahotki voy ey bormi yoqdir kim bilan nechta qancha
""".split())

_RU_WORDS = frozenset("""
i v ne chto eto kak ya ti mi vi oni no net vse tak je bi uje tolko yesli
kogda ochen privet spasibo pochemu gde kto mne tebe menya tebya yego yeyo yest
nas vas zdes tam seychas mojno nado bilo budet che chego kakoy kakaya tut
""".split())

_EN_WORDS = frozenset("""
the you and is are to of it this that what my your with for not but so just
have has was were will can do does dont im its be at on in we they he she
""".split())

_UZ_SUFFIX_RE = re.compile(
    r"(?:lar|larni|larga|lardan|larda|ning|ingiz|ingizni|imiz|yapti|yapman|yapsan"
    r"|yapsiz|gandan|ganda|gani|moqda|moqchi|mayman|madim|madi|dingiz|ibdi|ishdi"
    r"|sizmi|dimi|chilik|dagi|imni|ingni)$"
)


class LangScores(NamedTuple):
    uz: float
    ru: float
    en: float

    @property
    def is_uzbek(self) -> bool:
        return self.uz > 0 and self.uz > max(self.ru, self.en)


def _words(latin: str) -> list[str]:
    return [w.replace("'", "") for w in _WORD_RE.findall(latin)]


def scores(text: str) -> LangScores:
    if not text:
        return LangScores(0, 0, 0)

    uz = ru = en = 0.0
    uz += 2 * min(3, sum(1 for c in text if c in _UZ_CYR_LETTERS))
    ru += 2 * min(3, sum(1 for c in text if c in _RU_ONLY_LETTERS))

    latin = to_latin(text)
    has_cyrillic = any("а" <= c <= "я" or c in "ёў" for c in text.casefold())
    if not has_cyrillic:
        # o'/g' only means something when the user typed Latin themselves
        uz += 2 * min(3, len(_UZ_DIGRAPH_RE.findall(latin)))

    for word in _words(latin):
        if word in _UZ_WORDS:
            uz += 1
        elif len(word) > 4 and _UZ_SUFFIX_RE.search(word):
            uz += 0.5
        if word in _RU_WORDS and has_cyrillic:
            ru += 1
        if word in _EN_WORDS and not has_cyrillic:
            en += 1
    return LangScores(uz, ru, en)


def is_uzbek(text: str) -> bool:
    return scores(text).is_uzbek
