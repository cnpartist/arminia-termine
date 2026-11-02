# Arminia Termine Display Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hourly-rebuilt 1920×1080 PNG of the upcoming table soccer events in arminia.de style, published on GitHub Pages and set as wallpaper on the club's Windows PC.

**Architecture:** A stdlib-only Python build (`build.py` + small `termine/` modules) fetches the Terminliste, parses events, renders an HTML page with the site's fonts inlined, and screenshots it with headless Chrome into `site/`. A GitHub Actions workflow runs it hourly and deploys `site/` to Pages. PowerShell scripts on the club PC download the PNG and set it as wallpaper.

**Tech Stack:** Python 3 (stdlib, `unittest`), headless Chrome/Brave, GitHub Actions + Pages, PowerShell 5.1.

**Spec:** `docs/superpowers/specs/2026-11-02-arminia-termine-design.md`

## Global Constraints

- Python standard library only; tests with `python3 -m unittest discover -s tests`.
- Image 1920×1080; colours `#000` background, `#fff` text, `#005b9d` blue.
- Max 8 events; drop events dated before today in Europe/Berlin.
- Empty list copy: `Zurzeit keine Termine`. Footer copy: `Stand: <Wd> <DD.MM.YYYY>, <HH:MM>` and `arminia.de/tischfussball`.
- German weekday abbreviations: Mo Di Mi Do Fr Sa So.
- Fonts/crest fetched at build time only; never committed, never written to `site/`.
- Published URL base: `https://cnpartist.github.io/arminia-termine/`.
- Windows: no admin rights; per-user paths `%LOCALAPPDATA%\ArminiaTermine`, `%USERPROFILE%\Pictures\Arminia Termine\termine.png`.

## Review Focus

1. Titles with `&`, `<`, umlauts or `&nbsp;` → shown as plain readable text, HTML-escaped in the page (Task 1, Task 3 tests).
2. Very long title → stays on one line with an ellipsis, never pushes rows off the image (Task 3 test checks the CSS class; Task 4 visual check).
3. Event today earlier than now (e.g. 10:00 seen at 23:00) → still shown (Task 1 test).
4. Item with a date but no time → shows date, no time, no crash (Task 1 test).
5. arminia.de layout change (no event container / unreadable date) → build fails loudly instead of publishing "Zurzeit keine Termine" (Task 1 test).

---

### Task 1: Parse and select events

**Files:**
- Create: `termine/__init__.py`, `termine/parse.py`, `termine/select.py`
- Test: `tests/test_parse.py`, `tests/test_select.py`, fixture `tests/fixtures/terminliste.html` (the real page saved 2026-11-02)

**Interfaces:**
- Produces: `Event(start: datetime, has_time: bool, title: str)` (frozen dataclass, `start` naive local time); `parse_events(html: str) -> list[Event]`; `class LayoutChanged(Exception)`; `upcoming(events, today: date, limit: int = 8) -> list[Event]`.

- [ ] Step 1: tests — fixture yields 7 events, first `Event(datetime(2026,11,6,20,0), True, "Turnier: Offenes Doppel - Mini-Challenger")`, sixth title `Kickerturnier für Kids und Teens`; `<h3 class="event-title">21.11.2026<br>Foo &amp; Bar&nbsp;X</h3>` → `has_time False`, title `Foo & Bar X`; container with no items → `[]`; no `tx-sf-event-mgt` → `LayoutChanged`; item whose h3 has no date → `LayoutChanged`. `upcoming`: drops yesterday, keeps today 10:00, sorts by start, caps at `limit`.
- [ ] Step 2: run tests → fail (module missing).
- [ ] Step 3: implement with `html.parser.HTMLParser` collecting text of `h3.event-title` inside `div.tx-sf-event-mgt`, splitting on `<br>`; date regex `(\d{2})\.(\d{2})\.(\d{4})`, optional time `(\d{1,2}):(\d{2})`; whitespace (incl. nbsp) collapsed.
- [ ] Step 4: run tests → pass.
- [ ] Step 5: commit.

### Task 2: Site assets (fonts, crest)

**Files:**
- Create: `termine/assets.py`
- Test: `tests/test_assets.py`

**Interfaces:**
- Produces: `stylesheet_urls(html: str, base: str) -> list[str]` (absolute URLs of `<link rel="stylesheet">`); `crest_url(html: str, base: str) -> str | None` (img inside `#wappen`); `font_face_css(css: str) -> str` returning `@font-face` rules with only `format("woff2")` sources for family `Compacta` (any weight → 400) and `GillSans` weights 300, 700, 800; `""` if none found.

- [ ] Step 1: tests with a synthetic CSS containing a Compacta face and GillSans 300/400/700/800 faces each with eot+woff2+woff sources → output has 4 rules, contains `font/woff2` data URIs, contains no `vnd.ms-fontobject`, no GillSans 400; garbage CSS → `""`. URL helpers against the fixture: one `…/merged-….css` URL starting `https://www.arminia.de/`, crest ends with `arminia-wappen-2021.svg`.
- [ ] Step 2: run → fail. Step 3: implement (regex over `@font-face{…}` blocks). Step 4: run → pass. Step 5: commit.

### Task 3: Display page HTML

**Files:**
- Create: `termine/page.py`
- Test: `tests/test_page.py`

**Interfaces:**
- Consumes: `Event` (Task 1).
- Produces: `render_html(events: list[Event], now: datetime, fonts_css: str = "", crest_src: str | None = None) -> str`.

- [ ] Step 1: tests — titles appear HTML-escaped (`Foo &amp; Bar`); `Fr` + `06.11.` + `20:00` for the first fixture event; no time element text for `has_time=False`; empty list → `Zurzeit keine Termine`; footer `Stand: Mo 02.11.2026, 23:45` for `now=datetime(2026,11,2,23,45)`; `arminia.de/tischfussball` present; fonts_css inlined; no `<a ` and no `<script` in output; title element has class `title` (CSS: `white-space:nowrap; overflow:hidden; text-overflow:ellipsis`).
- [ ] Step 2: run → fail. Step 3: implement as one `string.Template`; layout 1920×1080, content inset left ≥160px, bottom ≥90px. Step 4: run → pass. Step 5: commit.

### Task 4: Build script + local end-to-end

**Files:**
- Create: `build.py`, `static/index.html`, `.gitignore` (`site/`, `__pycache__/`)

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: `python3 build.py [--out site] [--html-file FILE]` writes `site/termine.png`, `site/index.html`, `site/setup.ps1`, `site/update.ps1`; exit code ≠ 0 on fetch failure or `LayoutChanged`. Chrome from `$CHROME`, else first of `google-chrome`, `chromium`, `chromium-browser`, `brave-browser-stable` on PATH.

- [ ] Step 1: implement: `urllib` fetch with UA `arminia-termine-display (+https://github.com/cnpartist/arminia-termine)`, 30 s timeout, 3 attempts; asset failures only warn; render HTML to a temp dir outside `site/`; screenshot with `--headless=new --hide-scrollbars --force-device-scale-factor=1 --window-size=1920,1080 --virtual-time-budget=5000 --screenshot=…`; verify PNG is 1920×1080 by reading the IHDR. `index.html`: black page, `termine.png` with `object-fit:contain`, cache-busted reload every 10 min.
- [ ] Step 2: run `python3 build.py --out /tmp/…/site` with `CHROME=brave-browser-stable` → PNG exists; look at it; fix layout until it reads well (long titles, crest, fonts).
- [ ] Step 3: commit.

### Task 5: Windows scripts

**Files:**
- Create: `windows/update.ps1`, `windows/setup.ps1`

**Interfaces:**
- Consumes: published `termine.png`, `update.ps1`.
- Produces: scheduled task `Arminia Termine Hintergrund` (at logon of current user + hourly), wallpaper set via `SystemParametersInfo(SPI_SETDESKWALLPAPER=20, 0, path, SPIF_UPDATEINIFILE|SPIF_SENDCHANGE=3)`, `WallpaperStyle=6`, `TileWallpaper=0`, `Control Panel\Colors\Background="0 0 0"`.

- [ ] Step 1: `update.ps1`: TLS 1.2, download with cache-buster to temp, check PNG signature and size, replace only if hash differs, re-apply wallpaper only if changed or the registry `Wallpaper` value differs; any failure → exit 0 quietly.
- [ ] Step 2: `setup.ps1` (`-Uninstall` switch): download `update.ps1` into `%LOCALAPPDATA%\ArminiaTermine`, register task with action `conhost.exe --headless powershell.exe -NoProfile -ExecutionPolicy Bypass -File …`, run it once, print German instructions for the "Fotos" screensaver and open `control desk.cpl,,@screensaver`.
- [ ] Step 3: commit. (Not runnable on Linux; reviewed by reading.)

### Task 6: CI, Pages, docs

**Files:**
- Create: `.github/workflows/build.yml`, `README.md`

- [ ] Step 1: workflow: triggers `schedule: '7 * * * *'`, `push` to `main`, `workflow_dispatch`; job `build` (checkout@v7, unit tests, `python3 build.py --out site`, configure-pages@v6, upload-pages-artifact@v5) → job `deploy` (deploy-pages@v5, env `github-pages`); job `keepalive` on schedule: `gh api -X PUT repos/$REPO/actions/workflows/build.yml/enable`.
- [ ] Step 2: README: what it is, URLs, club PC install/uninstall, screensaver step, how it works, local build.
- [ ] Step 3: create public repo `cnpartist/arminia-termine`, enable Pages (build_type workflow), push; watch the run; fetch the published PNG and compare with the local one.
- [ ] Step 4: commit any fixes.
