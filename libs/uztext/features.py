"""
Text preparation shared by the Uzbek spam model's training and inference.

Changing this changes what the model sees: retrain after editing.
"""
from __future__ import annotations

import re

from .normalize import to_latin

_URL_RE = re.compile(r"(?:https?://|www\.)\S+|\b[\w-]+\.(?:uz|ru|com|me|org|net|io|xyz|info|top|click|link|shop)\b\S*")
_TG_LINK_RE = re.compile(r"\bt\.me/\S+|\btelegram\.me/\S+")
_MENTION_RE = re.compile(r"@\w{3,}")
_PHONE_RE = re.compile(r"(?:\+?998|\+7)?[\s\-()]*\d{2}[\s\-()]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}\b")
_MONEY_RE = re.compile(r"\d[\d\s.,]*\s*(?:\$|usd|so'm|som|сўм|сум|rubl|руб|mln|million|ming)", re.IGNORECASE)
_NUMBER_RE = re.compile(r"\d+")
_SPACE_RE = re.compile(r"\s+")


def prepare(text: str) -> str:
    """Lowercase Uzbek Latin with links, contacts and amounts as placeholders.

    Spammers rotate domains, usernames and phone numbers; the model should
    learn "has a contact" rather than a specific one.
    """
    text = _TG_LINK_RE.sub(" tglink ", text)
    text = _URL_RE.sub(" urllink ", text)
    text = _MENTION_RE.sub(" mention ", text)
    text = _PHONE_RE.sub(" phonenum ", text)
    text = _MONEY_RE.sub(" moneysum ", text)
    text = to_latin(text)
    text = _NUMBER_RE.sub("0", text)
    return _SPACE_RE.sub(" ", text).strip()
