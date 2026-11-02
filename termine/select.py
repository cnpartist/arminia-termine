"""Pick the events that belong on the display."""

from datetime import date

from termine.parse import Event


def upcoming(events: list[Event], today: date, limit: int = 8) -> list[Event]:
    """Events from today on (an event stays for its whole day), soonest first."""
    future = [e for e in events if e.start.date() >= today]
    return sorted(future, key=lambda e: e.start)[:limit]
