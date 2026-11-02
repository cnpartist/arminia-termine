#!/usr/bin/env python3
"""Build site/: termine.png from the arminia.de Terminliste, plus the viewer
page and the Windows scripts.

    python3 build.py [--out site] [--html-file saved-page.html]

Exits non-zero if the Terminliste can't be fetched or read, so a broken build
never replaces the last good image.
"""

import argparse
import base64
import mimetypes
import os
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from termine.assets import crest_url, font_face_css, stylesheet_urls
from termine.page import render_html
from termine.parse import LayoutChanged, parse_events
from termine.select import upcoming

SOURCE = "https://www.arminia.de/tischfussball/termine/terminliste"
USER_AGENT = "arminia-termine-display (+https://github.com/cnpartist/arminia-termine)"
TZ = ZoneInfo("Europe/Berlin")
ROOT = Path(__file__).resolve().parent
WIDTH, HEIGHT = 1920, 1080
CHROMES = ["google-chrome", "chromium", "chromium-browser", "brave-browser-stable"]


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def fetch(url: str, attempts: int = 3, timeout: int = 30) -> bytes:
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=timeout) as response:
                return response.read()
        except OSError as error:
            if attempt == attempts:
                raise
            log(f"retrying {url} ({error})")
            time.sleep(5 * attempt)


def load_assets(html: str) -> tuple[str, str | None]:
    """The site's fonts as @font-face CSS and the crest as a data URI.

    Failures only warn: fallback fonts / no crest beat not updating the dates.
    """
    fonts = ""
    try:
        for url in stylesheet_urls(html, SOURCE):
            fonts += font_face_css(fetch(url).decode("utf-8", "replace"))
    except OSError as error:
        log(f"warning: couldn't load the site's stylesheet ({error})")
    if not fonts:
        log("warning: site fonts not found, using fallback fonts")

    crest = None
    url = crest_url(html, SOURCE)
    if url:
        try:
            mime = mimetypes.guess_type(url.split("?")[0])[0] or "image/svg+xml"
            crest = f"data:{mime};base64," + base64.b64encode(fetch(url)).decode()
        except OSError as error:
            log(f"warning: couldn't load the crest ({error})")
    else:
        log("warning: crest not found on the page")
    return fonts, crest


def find_chrome() -> str:
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    for name in CHROMES:
        if path := shutil.which(name):
            return path
    raise SystemExit("error: no Chrome/Chromium found; set CHROME=/path/to/chrome")


def screenshot(html_path: Path, png_path: Path) -> None:
    # No --user-data-dir: Brave hangs in headless mode with a fresh profile.
    command = [
        find_chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", f"--window-size={WIDTH},{HEIGHT}",
        "--virtual-time-budget=5000", f"--screenshot={png_path}", html_path.as_uri(),
    ]
    if os.environ.get("CI"):
        command.insert(1, "--no-sandbox")  # GitHub's runners block Chrome's sandbox
    # Own process group, so a hung browser and all its helpers get killed on timeout.
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                               start_new_session=True)
    try:
        _, stderr = process.communicate(timeout=120)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()
        raise
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command, stderr=stderr)


def png_size(path: Path) -> tuple[int, int]:
    with open(path, "rb") as f:
        head = f.read(24)
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        raise ValueError(f"{path} is not a PNG")
    return struct.unpack(">II", head[16:24])


def build(out: Path, html: str) -> None:
    events = parse_events(html)
    now = datetime.now(TZ).replace(tzinfo=None)
    shown = upcoming(events, now.date())
    fonts, crest = load_assets(html)
    page = render_html(shown, now, fonts, crest)

    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:  # the page holds the fonts: never publish it
        page_path, png_path = Path(tmp) / "termine.html", Path(tmp) / "termine.png"
        page_path.write_text(page, encoding="utf-8")
        screenshot(page_path, png_path)
        if (size := png_size(png_path)) != (WIDTH, HEIGHT):
            raise SystemExit(f"error: screenshot is {size}, expected {(WIDTH, HEIGHT)}")
        shutil.copy(png_path, out / "termine.png")
    shutil.copy(ROOT / "static" / "index.html", out / "index.html")
    for script in sorted((ROOT / "windows").glob("*.ps1")):
        shutil.copy(script, out / script.name)
    log(f"{len(shown)} of {len(events)} events -> {out / 'termine.png'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", type=Path, default=ROOT / "site")
    parser.add_argument("--html-file", type=Path, help="use a saved Terminliste instead of fetching it")
    args = parser.parse_args()
    try:
        html = (args.html_file.read_text(encoding="utf-8") if args.html_file
                else fetch(SOURCE).decode("utf-8"))
        build(args.out, html)
    except (OSError, LayoutChanged, subprocess.SubprocessError) as error:
        raise SystemExit(f"error: {error}")


if __name__ == "__main__":
    main()
