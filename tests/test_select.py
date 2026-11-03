import unittest
from datetime import datetime

from termine.parse import Event
from termine.select import upcoming

NOW = datetime(2026, 11, 2, 18, 0)


def ev(y, m, d, h=20, title="T"):
    return Event(datetime(y, m, d, h, 0), True, title)


class UpcomingTest(unittest.TestCase):
    def test_drops_events_before_today(self):
        self.assertEqual(upcoming([ev(2026, 11, 1)], NOW), [])

    def test_drops_event_of_today_that_already_started(self):
        self.assertEqual(upcoming([ev(2026, 11, 2, h=12)], NOW), [])

    def test_keeps_event_of_today_starting_now_or_later(self):
        now, later = ev(2026, 11, 2, h=18), ev(2026, 11, 2, h=20)
        self.assertEqual(upcoming([now, later], NOW), [now, later])

    def test_keeps_event_of_today_without_time_all_day(self):
        all_day = Event(datetime(2026, 11, 2), False, "T")
        self.assertEqual(upcoming([all_day], NOW), [all_day])

    def test_drops_event_of_yesterday_without_time(self):
        self.assertEqual(upcoming([Event(datetime(2026, 11, 1), False, "T")], NOW), [])

    def test_sorts_by_start(self):
        a, b = ev(2026, 12, 1, title="a"), ev(2026, 11, 20, title="b")
        self.assertEqual(upcoming([a, b], NOW), [b, a])

    def test_sorts_across_year_boundary(self):
        jan, dec = ev(2027, 1, 3, title="jan"), ev(2026, 12, 30, title="dec")
        self.assertEqual(upcoming([jan, dec], NOW), [dec, jan])

    def test_caps_at_limit(self):
        events = [ev(2026, 11, d) for d in range(3, 20)]
        result = upcoming(events, NOW)
        self.assertEqual(len(result), 8)
        self.assertEqual(result[0].start.day, 3)
        self.assertEqual(len(upcoming(events, NOW, limit=3)), 3)


if __name__ == "__main__":
    unittest.main()
