"""Pick the events that belong on the display."""

from datetime import datetime

from termine.parse import Event


def upcoming(events: list[Event], now: datetime, limit: int = 8) -> list[Event]:
    """Events that haven't started yet, soonest first.

    An event without a time stays for its whole day.
    """
    def ahead(e: Event) -> bool:
        return e.start >= now if e.has_time else e.start.date() >= now.date()
    return sorted(filter(ahead, events), key=lambda e: e.start)[:limit]
