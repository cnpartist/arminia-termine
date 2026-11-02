import re
import unittest
from datetime import datetime

from termine.page import render_html
from termine.parse import Event

NOW = datetime(2026, 11, 2, 23, 45)
FIRST = Event(datetime(2026, 11, 6, 20, 0), True, "Turnier: Offenes Doppel - Mini-Challenger")


def text_of(html: str) -> str:
    """Visible text, roughly: tags removed, whitespace collapsed."""
    return " ".join(re.sub(r"<[^>]+>", " ", html.split("<body", 1)[1]).split())


class RenderHtmlTest(unittest.TestCase):
    def test_event_row_shows_weekday_date_time_title(self):
        visible = text_of(render_html([FIRST], NOW))
        self.assertIn("Fr 06.11. 20:00 Turnier: Offenes Doppel - Mini-Challenger", visible)

    def test_title_is_html_escaped(self):
        html = render_html([Event(datetime(2026, 11, 6, 20), True, "Foo & <Bar>")], NOW)
        self.assertIn("Foo &amp; &lt;Bar&gt;", html)
        self.assertNotIn("<Bar>", html)

    def test_event_without_time_shows_no_time(self):
        html = render_html([Event(datetime(2026, 11, 21), False, "Kids")], NOW)
        self.assertIn("Sa 21.11. Kids", text_of(html))
        self.assertNotIn("00:00", html)

    def test_no_events(self):
        self.assertIn("Zurzeit keine Termine", text_of(render_html([], NOW)))

    def test_footer(self):
        visible = text_of(render_html([FIRST], NOW))
        self.assertIn("Stand: Mo 02.11.2026, 23:45", visible)
        self.assertIn("arminia.de/tischfussball", visible)

    def test_fonts_and_crest_are_inlined(self):
        html = render_html([FIRST], NOW, fonts_css="@font-face{X}", crest_src="data:image/svg+xml;base64,AAA")
        self.assertIn("@font-face{X}", html)
        self.assertIn('src="data:image/svg+xml;base64,AAA"', html)

    def test_without_crest_there_is_no_img(self):
        self.assertNotIn("<img", render_html([FIRST], NOW))

    def test_no_links_or_scripts(self):
        html = render_html([FIRST], NOW)
        self.assertNotIn("<a ", html)
        self.assertNotIn("<script", html)

    def test_long_titles_are_cut_with_ellipsis(self):
        html = render_html([FIRST], NOW)
        self.assertIn('class="title"', html)
        rule = re.search(r"\.title\s*\{([^}]*)\}", html).group(1)
        for prop in ("white-space: nowrap", "overflow: hidden", "text-overflow: ellipsis"):
            self.assertIn(prop, rule)


if __name__ == "__main__":
    unittest.main()
