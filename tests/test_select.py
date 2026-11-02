import unittest
from datetime import date, datetime

from termine.parse import Event
from termine.select import upcoming


def ev(y, m, d, h=20, title="T"):
    return Event(datetime(y, m, d, h, 0), True, title)


class UpcomingTest(unittest.TestCase):
    def test_drops_events_before_today(self):
        self.assertEqual(upcoming([ev(2026, 11, 1)], date(2026, 11, 2)), [])

    def test_keeps_earlier_event_of_today(self):
        today_morning = ev(2026, 11, 2, h=10)
        self.assertEqual(upcoming([today_morning], date(2026, 11, 2)), [today_morning])

    def test_sorts_by_start(self):
        a, b = ev(2026, 12, 1, title="a"), ev(2026, 11, 20, title="b")
        self.assertEqual(upcoming([a, b], date(2026, 11, 2)), [b, a])

    def test_sorts_across_year_boundary(self):
        jan, dec = ev(2027, 1, 3, title="jan"), ev(2026, 12, 30, title="dec")
        self.assertEqual(upcoming([jan, dec], date(2026, 11, 2)), [dec, jan])

    def test_caps_at_limit(self):
        events = [ev(2026, 11, d) for d in range(3, 20)]
        result = upcoming(events, date(2026, 11, 2))
        self.assertEqual(len(result), 8)
        self.assertEqual(result[0].start.day, 3)
        self.assertEqual(len(upcoming(events, date(2026, 11, 2), limit=3)), 3)


if __name__ == "__main__":
    unittest.main()
