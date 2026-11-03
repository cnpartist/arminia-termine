"""Read the events from the arminia.de Terminliste HTML."""

import re
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser

DATE_RE = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")
TIME_RE = re.compile(r"(\d{1,2}):(\d{2})")


class LayoutChanged(Exception):
    """The page no longer looks the way this parser expects."""


@dataclass(frozen=True)
class Event:
    start: datetime  # local (Europe/Berlin) time, naive
    has_time: bool
    title: str
    description: str = ""


class _EventTitleCollector(HTMLParser):
    """Collects the text of every h3.event-title inside div.tx-sf-event-mgt,
    plus the text of the <p> paragraphs that follow it (the description).

    Each title is a list of text lines; <br> starts a new line.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found_container = False
        self.titles: list[list[str]] = []
        self.descriptions: list[str] = []
        self._div_depth = 0  # >0 while inside the container
        self._in_title = False
        self._p_depth = 0  # >0 while inside a description paragraph

    def handle_starttag(self, tag, attrs):
        classes = (dict(attrs).get("class") or "").split()
        if tag == "div":
            if self._div_depth:
                self._div_depth += 1
            elif "tx-sf-event-mgt" in classes:
                self.found_container = True
                self._div_depth = 1
        elif tag == "h3" and self._div_depth and "event-title" in classes:
            self._in_title = True
            self.titles.append([""])
            self.descriptions.append("")
        elif tag == "br" and self._in_title:
            self.titles[-1].append("")
        elif tag == "p" and self._div_depth and self.titles:
            self._p_depth += 1
            self.descriptions[-1] += " "

    def handle_endtag(self, tag):
        if tag == "div" and self._div_depth:
            self._div_depth -= 1
        elif tag == "h3":
            self._in_title = False
        elif tag == "p" and self._p_depth:
            self._p_depth -= 1

    def handle_data(self, data):
        if self._in_title:
            self.titles[-1][-1] += data
        elif self._p_depth:
            self.descriptions[-1] += data


def _clean(text: str) -> str:
    return " ".join(text.split())  # also collapses non-breaking spaces


def _to_event(lines: list[str], description: str) -> Event:
    lines = [_clean(line) for line in lines if _clean(line)]
    if not lines:
        raise LayoutChanged("empty event title")
    when, title = lines[0], " ".join(lines[1:])
    date_match = DATE_RE.search(when)
    if not date_match or not title:
        raise LayoutChanged(f"can't read event heading: {' / '.join(lines)!r}")
    day, month, year = (int(g) for g in date_match.groups())
    time_match = TIME_RE.search(when, date_match.end())
    hour, minute = (int(g) for g in time_match.groups()) if time_match else (0, 0)
    return Event(datetime(year, month, day, hour, minute), bool(time_match), title,
                 _clean(description))


def parse_events(html: str) -> list[Event]:
    collector = _EventTitleCollector()
    collector.feed(html)
    collector.close()
    if not collector.found_container:
        raise LayoutChanged("event list container (div.tx-sf-event-mgt) not found")
    return [_to_event(lines, description)
            for lines, description in zip(collector.titles, collector.descriptions)]
