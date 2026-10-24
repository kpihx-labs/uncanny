"""Simple sentence tokenizer that avoids requiring nltk."""

from __future__ import annotations

import re

_ABBREVS = {"Mr", "Mrs", "Ms", "Dr", "Prof", "Sr", "Jr", "St", "vs", "etc", "Inc", "Ltd", "Corp"}

# Split on sentence-ending punctuation followed by whitespace and uppercase
_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"\'\u201c])")


def split_sentences(text: str) -> list[tuple[str, int, int]]:
    """Split text into sentences, returning (text, start, end) tuples."""
    # PDF extraction commonly inserts newlines, form feeds and uneven spacing
    # between sentences. Normalize before splitting so reconstructed abbreviations
    # retain searchable offsets in this analysis string.
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    # First pass: split on regex
    raw_parts = _SPLIT_RE.split(text)

    # Second pass: rejoin splits that were after abbreviations or decimals
    merged: list[str] = []
    for part in raw_parts:
        if merged and _should_rejoin(merged[-1], part):
            merged[-1] = merged[-1] + " " + part
        else:
            merged.append(part)

    # Build results with offsets
    results: list[tuple[str, int, int]] = []
    pos = 0
    for part in merged:
        part = part.strip()
        if not part:
            continue
        start = text.index(part, pos)
        end = start + len(part)
        results.append((part, start, end))
        pos = end

    return results


def _should_rejoin(prev: str, _next: str) -> bool:
    """Check if a split was caused by an abbreviation or decimal."""
    prev = prev.rstrip()
    if not prev.endswith("."):
        return False

    # Check for decimal numbers (e.g., "3.14" split after "3.")
    if len(prev) >= 2 and prev[-2].isdigit():
        return True

    # Check for abbreviations
    last_word = prev.rstrip(".").rsplit(None, 1)[-1] if prev.rstrip(".") else ""
    if last_word in _ABBREVS:
        return True

    return False
