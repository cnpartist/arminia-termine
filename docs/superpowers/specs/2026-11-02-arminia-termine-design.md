# Arminia Tischfußball – event display (design)

Date: 2026-11-02 · Status: approved by Markus (via Telegram)

## Goal

The table soccer department's club rooms have a Windows PC with two screens.
Screen 2 shows live tournament standings while a tournament runs. When nothing
else is on it, it should show the upcoming events from
<https://www.arminia.de/tischfussball/termine/terminliste>, in the look of
arminia.de, without menus, links or buttons: just dates and titles.

Decisions made with Markus:

- Delivered as the **desktop background on all screens**, plus optionally the
  built-in Windows **"Fotos" (Photos) screensaver** showing the same image.
  Whatever isn't covered by a window shows the dates; standings simply go on top.
- **Source: the website only** for now. Extra dates not on the website are a
  later extension (not built now).
- Built and hosted on **GitHub (Actions + Pages)** in a public repo
  `cnpartist/arminia-termine`, independent of tinky.

## What the image shows

PNG, 1920×1080, styled like arminia.de (black background, white text,
club blue `#005b9d`, the site's fonts Compacta and Gill Sans, the crest):

- Header: crest and "Termine" in Compacta (changed 2026-11-03 at Markus's
  request; first version had "Tischfußball" and a blue bar "Termine")
- Up to 8 upcoming events, each: weekday + date, time, the title in bold
  uppercase Gill Sans and, on a second line, the website's description in
  light Gill Sans (as on the site). Both drop a leading "Turnier:" and any
  "- Mini-Challenger" (2026-11-03, Markus's request). The second line also
  drops what the row already shows: the event's own date at its start and the
  title at its start or end (punctuation and case ignored); if under two words
  are left after dropping the title, the second line is left out. Rows are
  separated by 4px blue rules, like the site. No frame around the list: the
  dates line up with the crest's left edge (2026-11-03, Markus's request, along
  with slightly bigger text).
- Footer: "Stand: <weekday> <date>, <time>" (Europe/Berlin) and
  "arminia.de/tischfussball"
- No upcoming events → "Zurzeit keine Termine"
- Layout keeps clear of the Windows taskbar (bottom ~80px) and desktop icons
  (left edge), since it's a desktop background.

Events dated before today (Berlin time) are dropped; an event stays visible for
its whole day.

## Architecture

```
GitHub Actions (hourly cron, on push, manual)
  build.py
    fetch Terminliste HTML ──► parse.py ──► [Event(start, has_time, title, description)]
    fetch site CSS + crest ──► assets.py ──► @font-face CSS (woff2 only), crest data URI
    page.py: events + now + assets ──► display HTML (fonts inline, never published)
    headless Chrome screenshot ──► site/termine.png
    copy index.html, windows/*.ps1 ──► site/
  deploy site/ to GitHub Pages
        │  https://cnpartist.github.io/arminia-termine/termine.png
        ▼
Club PC: scheduled task (at logon + hourly) runs update.ps1
  download → validate PNG → Pictures\Arminia Termine\termine.png
  → set as wallpaper (all screens, "Fit", black background colour)
"Fotos" screensaver pointed at the same folder (manual one-time step)
```

Units:

| Unit | Responsibility | Depends on |
|---|---|---|
| `termine/parse.py` | `parse_events(html) -> list[Event]`; raises `LayoutChanged` if the event list container is missing or an item can't be read | stdlib only |
| `termine/select.py` | `upcoming(events, today, limit)` – drop past, sort, cap | – |
| `termine/assets.py` | `font_face_css(css_text)` extracts woff2 faces for Compacta / GillSans; `stylesheet_urls(html)`, `crest_url(html)` | stdlib only |
| `termine/page.py` | `render_html(events, now, fonts_css, crest_data_uri) -> str` | – |
| `build.py` | orchestration: HTTP fetches (timeouts, retries, polite User-Agent), Chrome screenshot, writing `site/` | Chrome on PATH or `$CHROME` |
| `site_static/index.html` | full-screen viewer of `termine.png`, reloads every 10 min | – |
| `windows/update.ps1` | download + validate + set wallpaper | PowerShell 5.1 |
| `windows/setup.ps1` | install `update.ps1`, register scheduled task, run once, explain screensaver step; `-Uninstall` removes it | PowerShell 5.1 |

Python: standard library only (no pip installs), so it runs on the stock
Ubuntu runner and on tinky.

## Fonts and crest

Compacta and Gill Sans are commercial fonts. They are downloaded from arminia.de
at build time (the site's merged CSS embeds them as data URIs) and only used to
draw the PNG. They are never committed or published. If extraction fails, the
build continues with fallback fonts (Arial Narrow / Arial) and logs a warning:
a slightly-off font beats stale dates. Same for the crest: missing → no crest.

## Error handling

- Terminliste unreachable (after retries) or `LayoutChanged` → build fails →
  Pages keeps the last good deploy; GitHub emails the repo owner about the
  failed scheduled run.
- Container present but no items → legitimate "Zurzeit keine Termine".
- Club PC offline / download fails / file isn't a PNG → keep the current image,
  exit quietly.
- Public repos disable scheduled workflows after 60 days without activity: the
  workflow re-enables itself via the API (keepalive), but only when neither a
  commit nor a re-enable happened in the last 45 days. Re-enabling it every
  hour seemed to stall the schedule (2026-11-03).

## Club PC details

- No admin rights needed; everything is per user (`%LOCALAPPDATA%\ArminiaTermine`,
  HKCU registry, a scheduled task for the current user).
- Task runs via `conhost.exe --headless powershell.exe …` so no console window
  flashes up on the display.
- Wallpaper style "Fit" (6) with black desktop colour: other aspect ratios get
  black bars that blend with the black image.
- Wallpaper is only re-applied when the image changed or the background was
  changed by someone else.
- Install: `irm https://cnpartist.github.io/arminia-termine/setup.ps1 | iex` in
  PowerShell (or download and "Run with PowerShell").

## Testing

- Unit tests (stdlib `unittest`) for parsing (saved real page as fixture, plus
  edge cases: no time, empty list, missing container), selection, font
  extraction and HTML rendering.
- Local end-to-end build on tinky with Brave headless, visual check of the PNG.
- CI runs the tests before building.
- The PowerShell scripts can't be run here; Markus tests them on the club PC.

## Out of scope (later)

- Additional dates not on the website (separate source, merged in).
- Per-screen wallpapers, custom screensaver program.
