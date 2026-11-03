import unittest
from datetime import date

from termine.clean import clean, short_description

DAY = date(2026, 11, 21)


class CleanTest(unittest.TestCase):
    def test_drops_turnier_prefix_and_mini_challenger(self):
        self.assertEqual(clean("Turnier: Offenes Doppel - Mini-Challenger"), "Offenes Doppel")

    def test_mini_challenger_spelling_variants(self):
        self.assertEqual(clean("Turnier: Offenes Einzel- Mini-Challenger"), "Offenes Einzel")
        self.assertEqual(clean("Turnier: Monster-DYP - Mini Challenger"), "Monster-DYP")
        self.assertEqual(clean("Turnier: Monster-DYP - MINI-CHALLENGER"), "Monster-DYP")

    def test_plain_challenger_stays(self):
        self.assertEqual(clean("Turnier: Challenger - Damen Doppel"), "Challenger - Damen Doppel")

    def test_mini_challenger_in_the_middle_of_a_description(self):
        self.assertEqual(
            clean("Turnier: Offenes Doppel- Mini-Challenger - Einlass: 19:30, Start: 20:00"),
            "Offenes Doppel - Einlass: 19:30, Start: 20:00",
        )

    def test_turnier_only_as_prefix(self):
        self.assertEqual(clean("Kickerturnier für Kids und Teens"), "Kickerturnier für Kids und Teens")
        self.assertEqual(clean("Großes Turnier: Finale"), "Großes Turnier: Finale")

    def test_never_cleans_a_text_down_to_nothing(self):
        self.assertEqual(clean("Turnier:"), "Turnier:")

    def test_empty_stays_empty(self):
        self.assertEqual(clean(""), "")


class ShortDescriptionTest(unittest.TestCase):
    def test_drops_title_repeated_at_the_start(self):
        self.assertEqual(
            short_description("Offenes Doppel - Einlass: 19:30, Start: 20:00", "Offenes Doppel", DAY),
            "Einlass: 19:30, Start: 20:00")

    def test_repeat_may_differ_in_punctuation_and_case(self):
        self.assertEqual(
            short_description("Challenger: Damen Einzel- Einlass: 10:30", "Challenger - Damen Einzel", DAY),
            "Einlass: 10:30")
        self.assertEqual(
            short_description("MONSTER-DYP - Einlass: 19:30", "Monster DYP", DAY), "Einlass: 19:30")

    def test_drops_title_repeated_at_the_end(self):
        self.assertEqual(
            short_description("Anmeldung bis 18 Uhr - Offenes Doppel", "Offenes Doppel", DAY),
            "Anmeldung bis 18 Uhr")

    def test_drops_the_events_own_date(self):
        self.assertEqual(short_description("21.11. - Schläger mitbringen", "Kids", DAY), "Schläger mitbringen")
        self.assertEqual(short_description("21.11.2026: Schläger mitbringen", "Kids", DAY), "Schläger mitbringen")

    def test_keeps_a_different_date(self):
        self.assertEqual(short_description("28.11. Ersatztermin", "Kids", DAY), "28.11. Ersatztermin")

    def test_pure_repeat_disappears(self):
        self.assertEqual(short_description("Offenes Doppel", "Offenes Doppel", DAY), "")
        self.assertEqual(
            short_description("21.11. - Offenes Kickerturnier für Kids und Teens",
                              "Kickerturnier für Kids und Teens", DAY), "")

    def test_title_in_the_middle_stays(self):
        self.assertEqual(short_description("Heute Offenes Doppel mit Grill", "Offenes Doppel", DAY),
                         "Heute Offenes Doppel mit Grill")

    def test_unrelated_descriptions_stay(self):
        self.assertEqual(short_description("Bitte Schläger mitbringen", "Vereinsabend", DAY),
                         "Bitte Schläger mitbringen")
        self.assertEqual(short_description("Ausgebucht", "Vereinsabend", DAY), "Ausgebucht")
        self.assertEqual(short_description("", "Vereinsabend", DAY), "")


if __name__ == "__main__":
    unittest.main()
