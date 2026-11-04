# Arminia Tischfußball – Termine display

The upcoming events from the
[Terminliste on arminia.de](https://www.arminia.de/tischfussball/termine/terminliste)
as a 1920×1080 image in the website's look, for the screens in the club rooms.
It's set as the desktop background (and optionally the screensaver) of the
club PC, so the dates show whenever no window covers the screen.

- Image: <https://cnpartist.github.io/arminia-termine/termine.png>
- Full-screen page: <https://cnpartist.github.io/arminia-termine/>

The image is rebuilt by GitHub Actions every day at 6:00 and 18:00 (German
time), on every push, and from the Actions tab ("Run workflow"). Events that
have already started are left out. If arminia.de is down or its page layout
changes, the build fails, the last good image stays online, and GitHub emails
the repo owner.

## Club PC (Windows)

Open PowerShell (no admin rights needed) and run:

```powershell
irm https://cnpartist.github.io/arminia-termine/setup.ps1 | iex
```

This saves `update.ps1` to `%LOCALAPPDATA%\ArminiaTermine` and creates the
scheduled task **Arminia Termine Hintergrund**. The task runs at logon and
every hour, downloads the image to `Bilder\Arminia Termine\termine.png`, and
sets it as the background on all screens. When the PC is offline, the last
image stays.

**Screensaver (optional):** setup opens the screensaver settings. Pick
"Fotos", then under "Einstellungen…" choose the folder `Bilder\Arminia Termine`.

**Remove:**

```powershell
irm https://cnpartist.github.io/arminia-termine/uninstall.ps1 | iex
```

## How it works

| File | Job |
|---|---|
| `termine/parse.py` | Reads date, time, title and description of each event from the Terminliste HTML |
| `termine/clean.py` | Drops "Turnier:" and "- Mini-Challenger"; drops title and date repeats from the description |
| `termine/select.py` | Keeps events that haven't started yet (all-day ones for their whole day), soonest first, at most 8 |
| `termine/assets.py` | Finds the site's fonts (Compacta, Gill Sans) and the crest |
| `termine/page.py` | The 1920×1080 display page |
| `build.py` | Fetches everything, screenshots the page with headless Chrome into `site/` |
| `static/index.html` | Full-screen viewer for the image, reloads every 10 minutes |
| `windows/*.ps1` | Setup, hourly update and uninstall on the club PC |
| `server/*` | systemd timer that starts the build at 6:00 and 18:00 |

The fonts are licensed. They're downloaded from arminia.de while the image is
drawn and are never stored in this repo or published. If they can't be loaded,
the image falls back to Arial.

## Build timer

GitHub's own schedule fires unreliably for this repo, so a Linux machine that's
always on starts the 6:00 and 18:00 builds with a systemd user timer
(`server/`). GitHub's schedule stays in the workflow as a backup. Needs `gh`
logged in with the `workflow` scope:

```sh
cp server/arminia-termine-build.* ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now arminia-termine-build.timer
loginctl enable-linger "$USER"   # keep user timers running while logged out
```

`systemctl --user list-timers` shows the next start;
`systemctl --user start arminia-termine-build.service` builds right away.

## Local build

Needs Python 3.11+ and Chrome, Chromium or Brave (or set `CHROME=/path/to/browser`).

```sh
python3 -m unittest discover -s tests
python3 build.py --out site        # writes site/termine.png
```
