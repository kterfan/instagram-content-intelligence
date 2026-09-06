"""Conservative comparison keys; never use these to overwrite display copy."""
from __future__ import annotations

import re
import unicodedata

_LETTERS = str.maketrans("يكى", "یکی")
_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def comparison_key(text: str) -> str:
    """Unify Arabic/Persian letters, digits and word separators for matching.

    Diacritics and punctuation are preserved. ZWNJ becomes a space, so joined
    spellings are deliberately not guessed. Original strings remain evidence.
    """
    normalized = unicodedata.normalize("NFC", text).translate(_LETTERS).translate(_DIGITS)
    return re.sub(r"\s+", " ", normalized.replace("\u200c", " ")).strip().casefold()


def contains_phrase(text: str, phrase: str) -> bool:
    key = comparison_key(phrase)
    return bool(key and re.search(r"(?<!\w)" + re.escape(key) + r"(?!\w)", comparison_key(text)))
