"""Shorten event texts for the display: no "Turnier:" prefix, no "- Mini-Challenger"."""

import re

PREFIX_RE = re.compile(r"^\s*Turnier:\s*", re.IGNORECASE)
MINI_CHALLENGER_RE = re.compile(r"\s*-\s*Mini[\s-]*Challenger\b", re.IGNORECASE)


def clean(text: str) -> str:
    cleaned = MINI_CHALLENGER_RE.sub("", PREFIX_RE.sub("", text))
    cleaned = " ".join(cleaned.split())
    return cleaned or text
