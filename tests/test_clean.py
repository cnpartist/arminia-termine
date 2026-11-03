import unittest

from termine.clean import clean


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


if __name__ == "__main__":
    unittest.main()
