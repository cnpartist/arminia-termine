"""Find arminia.de's fonts and crest so the display looks like the website.

The fonts (Compacta, Gill Sans) are licensed: they're only used while drawing
the image and are never stored in the repo or published.
"""

import re
from html.parser import HTMLParser
from urllib.parse import urljoin

FACE_RE = re.compile(r"@font-face\s*\{(.*?)\}", re.S)
FAMILY_RE = re.compile(r"font-family:\s*[\"']?([^\"';}]+)")
WEIGHT_RE = re.compile(r"font-weight:\s*(\w+)")
WOFF2_RE = re.compile(r'url\(\s*["\']?data:[\w/.+-]*woff2[^,]*base64,([A-Za-z0-9+/=]+)')

GILL_SANS_WEIGHTS = {"300", "700", "800"}


def _face_rule(family: str, weight: str, woff2_b64: str) -> str:
    return (
        f'@font-face{{font-family:"{family}";font-weight:{weight};font-style:normal;'
        f'src:url(data:font/woff2;base64,{woff2_b64}) format("woff2")}}'
    )


def font_face_css(css: str) -> str:
    """@font-face rules (woff2 only) for Compacta and Gill Sans 300/700/800."""
    rules, have_compacta = [], False
    for body in FACE_RE.findall(css):
        family_match = FAMILY_RE.search(body)
        weight_match = WEIGHT_RE.search(body)
        woff2_match = WOFF2_RE.search(body)
        if not (family_match and woff2_match):
            continue
        family = family_match.group(1).strip()
        weight = weight_match.group(1) if weight_match else "normal"
        if family == "Compacta" and not have_compacta:
            rules.append(_face_rule("Compacta", "400", woff2_match.group(1)))
            have_compacta = True
        elif family == "GillSans" and weight in GILL_SANS_WEIGHTS:
            rules.append(_face_rule("GillSans", weight, woff2_match.group(1)))
    return "\n".join(rules)


class _LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stylesheets: list[str] = []
        self.crest: str | None = None
        self._in_wappen = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "link" and "stylesheet" in (a.get("rel") or "").split() and a.get("href"):
            self.stylesheets.append(a["href"])
        elif tag == "div":
            if self._in_wappen:
                self._in_wappen += 1
            elif a.get("id") == "wappen":
                self._in_wappen = 1
        elif tag == "img" and self._in_wappen and self.crest is None and a.get("src"):
            self.crest = a["src"]

    def handle_endtag(self, tag):
        if tag == "div" and self._in_wappen:
            self._in_wappen -= 1


def _collect(html: str) -> _LinkCollector:
    collector = _LinkCollector()
    collector.feed(html)
    collector.close()
    return collector


def stylesheet_urls(html: str, base: str) -> list[str]:
    return [urljoin(base, href) for href in _collect(html).stylesheets]


def crest_url(html: str, base: str) -> str | None:
    src = _collect(html).crest
    return urljoin(base, src) if src else None
