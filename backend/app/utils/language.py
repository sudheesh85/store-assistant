from __future__ import annotations

from functools import lru_cache
from typing import Literal

from langdetect import DetectorFactory, detect

DetectorFactory.seed = 0  # Make detection deterministic

LanguageCode = Literal["ml", "en", "unknown"]


@lru_cache(maxsize=256)
def detect_language(text: str) -> LanguageCode:
    """Detect Malayalam (ml) vs English (en); fall back to unknown."""
    if not text:
        return "unknown"
    try:
        code = detect(text)
    except Exception:
        return "unknown"
    if code.startswith("ml"):
        return "ml"
    if code.startswith("en"):
        return "en"
    return "unknown"


def should_respond_in_malayalam(text: str) -> bool:
    """Decide whether to craft the response in Malayalam."""
    lang = detect_language(text)
    if lang == "ml":
        return True
    if lang == "unknown":
        # Heuristic: presence of Malayalam characters or Manglish keywords
        malayalam_chars = any("\u0d00" <= ch <= "\u0d7f" for ch in text)
        manglish_keywords = {"entha", "vila", "vilpana", "vilpanam", "sambhavam", "stock"}
        if malayalam_chars:
            return True
        if any(word in text.lower() for word in manglish_keywords):
            return True
    return False


__all__ = ["detect_language", "should_respond_in_malayalam"]
