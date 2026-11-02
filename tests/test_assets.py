import re
import unittest
from pathlib import Path

from termine.assets import crest_url, font_face_css, stylesheet_urls

FIXTURE = Path(__file__).parent / "fixtures" / "terminliste.html"
BASE = "https://www.arminia.de/tischfussball/termine/terminliste"


def face(family: str, weight: str, tag: str) -> str:
    """A @font-face shaped like the ones in arminia.de's merged CSS."""
    return (
        f'@font-face{{font-family:"{family}";'
        f'src:url("data:application/vnd.ms-fontobject;charset=utf-8;base64,EOT{tag}");'
        f'src:url("data:application/vnd.ms-fontobject;charset=utf-8;base64,EOT{tag}?#iefix") format("embedded-opentype"),'
        f'url("data:application/font-woff2;charset=utf-8;base64,W2{tag}") format("woff2"),'
        f'url("data:application/font-woff;charset=utf-8;base64,W1{tag}") format("woff");'
        f"font-weight:{weight};font-style:normal;font-display:swap}}"
    )


SITE_CSS = "body{background:#000}" + "".join([
    face("Compacta", "normal", "c"),
    face("Compacta", "bold", "cb"),
    face("GillSans", "400", "g4"),
    face("GillSans", "300", "g3"),
    face("GillSans", "700", "g7"),
    face("GillSans", "800", "g8"),
]) + "h2{color:#fff}"


class FontFaceCssTest(unittest.TestCase):
    def setUp(self):
        self.css = font_face_css(SITE_CSS)

    def test_keeps_compacta_and_three_gill_sans_weights(self):
        self.assertEqual(self.css.count("@font-face"), 4)
        for tag in ("W2c", "W2g3", "W2g7", "W2g8"):
            self.assertIn(f"data:font/woff2;base64,{tag}", self.css)

    def test_drops_other_formats_and_weights(self):
        self.assertNotIn("vnd.ms-fontobject", self.css)
        self.assertNotIn("W1", self.css)  # woff (v1)
        self.assertNotIn("W2g4", self.css)  # GillSans 400
        self.assertNotIn("W2cb", self.css)  # second Compacta face

    def test_weights_are_declared(self):
        weights = re.findall(r'font-family:"(\w+)";font-weight:(\d+)', self.css)
        self.assertEqual(sorted(weights), [
            ("Compacta", "400"), ("GillSans", "300"), ("GillSans", "700"), ("GillSans", "800"),
        ])

    def test_garbage_gives_empty_string(self):
        self.assertEqual(font_face_css("not css at all"), "")


class UrlHelpersTest(unittest.TestCase):
    def setUp(self):
        self.html = FIXTURE.read_text(encoding="utf-8")

    def test_stylesheet_urls_are_absolute(self):
        [url] = stylesheet_urls(self.html, BASE)
        self.assertTrue(url.startswith("https://www.arminia.de/typo3temp/assets/compressed/merged-"))

    def test_crest_url(self):
        url = crest_url(self.html, BASE)
        self.assertTrue(url.startswith("https://www.arminia.de/"))
        self.assertTrue(url.endswith("arminia-wappen-2021.svg"))

    def test_crest_url_missing(self):
        self.assertIsNone(crest_url("<html></html>", BASE))


if __name__ == "__main__":
    unittest.main()
