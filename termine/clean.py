"""Shorten event texts for the display: no "Turnier:" prefix, no "- Mini-Challenger",
and no second line that only repeats the title or the date."""

import re
from datetime import date

PREFIX_RE = re.compile(r"^\s*Turnier:\s*", re.IGNORECASE)
MINI_CHALLENGER_RE = re.compile(r"\s*-\s*Mini[\s-]*Challenger\b", re.IGNORECASE)
DATE_PREFIX_RE = re.compile(r"^(\d{1,2})\.(\d{1,2})\.(?:\d{4}|\d{2})?(?!\d)")
SEPARATORS = " -–:,;"


def clean(text: str) -> str:
    cleaned = MINI_CHALLENGER_RE.sub("", PREFIX_RE.sub("", text))
    cleaned = " ".join(cleaned.split())
    return cleaned or text


def short_description(description: str, title: str, day: date) -> str:
    """The description without what the display already shows.

    Drops a leading date when it's the event's own date, and the title when the
    description starts or ends with it (punctuation and case don't matter). If
    the title was dropped and less than two words are left, the whole
    description was a repeat and nothing is returned.
    """
    text = description.strip()
    date_match = DATE_PREFIX_RE.match(text)
    if date_match and (int(date_match[1]), int(date_match[2])) == (day.day, day.month):
        text = text[date_match.end():].lstrip(SEPARATORS)

    words = re.findall(r"\w+", title)
    if not words:
        return text
    title_re = r"\W*".join(map(re.escape, words))
    repeat = (re.match(title_re + r"(?!\w)", text, re.IGNORECASE)
              or re.search(r"(?<!\w)" + title_re + r"\W*$", text, re.IGNORECASE))
    if not repeat:
        return text
    rest = (text[:repeat.start()] + text[repeat.end():]).strip(SEPARATORS)
    return rest if len(re.findall(r"\w+", rest)) >= 2 else ""
