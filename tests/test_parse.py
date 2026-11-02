import unittest
from datetime import datetime
from pathlib import Path

from termine.parse import Event, LayoutChanged, parse_events

FIXTURE = Path(__file__).parent / "fixtures" / "terminliste.html"


def page(items_html: str) -> str:
    return (
        '<html><body><div class="tx-sf-event-mgt">'
        + items_html
        + "</div></body></html>"
    )


def item(h3_inner: str) -> str:
    return (
        '<div class="event-list-item"><div class="event-list-row">'
        f'<h3 class="event-title">{h3_inner}</h3></div>'
        '<div class="event-list-row"><p>Beschreibung</p></div></div>'
    )


class ParseRealPageTest(unittest.TestCase):
    def setUp(self):
        self.events = parse_events(FIXTURE.read_text(encoding="utf-8"))

    def test_finds_all_seven_events(self):
        self.assertEqual(len(self.events), 7)

    def test_first_event_has_date_time_and_title(self):
        self.assertEqual(
            self.events[0],
            Event(datetime(2026, 11, 6, 20, 0), True,
                  "Turnier: Offenes Doppel - Mini-Challenger"),
        )

    def test_title_with_umlaut(self):
        self.assertEqual(self.events[5].title, "Kickerturnier für Kids und Teens")
        self.assertEqual(self.events[5].start, datetime(2026, 11, 21, 10, 0))


class ParseEdgeCasesTest(unittest.TestCase):
    def test_date_without_time(self):
        [ev] = parse_events(page(item("21.11.2026<br>Foo &amp; Bar&nbsp;X")))
        self.assertFalse(ev.has_time)
        self.assertEqual(ev.start, datetime(2026, 11, 21, 0, 0))
        self.assertEqual(ev.title, "Foo & Bar X")

    def test_whitespace_is_collapsed(self):
        [ev] = parse_events(page(item("\n  06.11.2026 - 20:00<br>\n  A   <b>B</b>\n")))
        self.assertEqual(ev.title, "A B")

    def test_empty_container_means_no_events(self):
        self.assertEqual(parse_events(page("")), [])

    def test_missing_container_is_layout_change(self):
        with self.assertRaises(LayoutChanged):
            parse_events("<html><body><h3 class='event-title'>06.11.2026<br>X</h3></body></html>")

    def test_unreadable_date_is_layout_change(self):
        with self.assertRaises(LayoutChanged):
            parse_events(page(item("Demnächst<br>Turnier")))


if __name__ == "__main__":
    unittest.main()
