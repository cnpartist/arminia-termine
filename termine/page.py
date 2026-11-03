"""The display page (1920×1080) that gets screenshotted into termine.png."""

from datetime import datetime
from html import escape
from string import Template

from termine.clean import clean
from termine.parse import Event

WEEKDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

# The left inset keeps desktop icons off the text; the bottom inset keeps the
# Windows taskbar off the footer.
PAGE = Template("""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Tischfußball – Termine</title>
<style>
$fonts_css
:root {
  --blue: #005b9d;
  --white: #fff;
  --grey: #a9b3ba;
  --display: "Compacta", "Arial Narrow", "Liberation Sans Narrow", sans-serif;
  --text: "GillSans", "Gill Sans MT", "Gill Sans", Arial, sans-serif;
}
html, body {
  margin: 0;
  width: 1920px;
  height: 1080px;
  overflow: hidden;
  background: #000;
  color: var(--white);
  font-family: var(--text);
}
.frame {
  position: absolute;
  left: 160px;
  right: 120px;
  top: 56px;
  bottom: 104px;
  display: flex;
  flex-direction: column;
}
header {
  display: flex;
  align-items: center;
  gap: 40px;
  height: 136px;
  flex: none;
}
header img { height: 136px; width: auto; }
h1 {
  margin: 0;
  font-family: var(--display);
  font-weight: 400;
  font-size: 156px;
  line-height: 1;
  text-transform: uppercase;
}
.box {
  flex: 1;
  min-height: 0;
  margin-top: 28px;
  border: 1px solid var(--blue);
  padding: 6px 48px;
}
ol {
  list-style: none;
  margin: 0;
  padding: 0;
  height: 100%;
  display: grid;
  grid-template-rows: repeat(8, 1fr);
}
li {
  display: grid;
  grid-template-columns: 230px 170px 1fr;
  align-items: center;
  min-width: 0;
  border-bottom: 4px solid var(--blue);
}
li:last-child { border-bottom: none; }
.when, .time {
  font-family: var(--display);
  font-size: 72px;
  line-height: 1;
  padding-top: .06em;
  white-space: nowrap;
}
.time { color: var(--grey); }
.text { min-width: 0; }
.title {
  display: block;
  font-weight: 700;
  font-size: 38px;
  line-height: 1.15;
  letter-spacing: .025em;
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.desc {
  display: block;
  margin-top: 2px;
  font-weight: 300;
  font-size: 30px;
  line-height: 1.15;
  letter-spacing: .1em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
li.empty {
  grid-template-columns: 1fr;
  font-weight: 300;
  font-size: 44px;
  letter-spacing: .04em;
  color: var(--grey);
}
footer {
  position: absolute;
  left: 160px;
  right: 120px;
  bottom: 56px;
  display: flex;
  justify-content: space-between;
  font-weight: 300;
  font-size: 26px;
  letter-spacing: .05em;
  color: var(--grey);
}
</style>
</head>
<body>
<div class="frame">
  <header>$crest<h1>Termine</h1></header>
  <div class="box"><ol>
$rows
  </ol></div>
</div>
<footer><span>Stand: $stand</span><span>arminia.de/tischfussball</span></footer>
</body>
</html>
""")


def _row(event: Event) -> str:
    start = event.start
    when = f"{WEEKDAYS[start.weekday()]} {start:%d.%m.}"
    time = f"{start:%H:%M}" if event.has_time else ""
    desc = (f'<span class="desc">{escape(clean(event.description))}</span>'
            if event.description else "")
    return (
        f'    <li><span class="when">{when}</span>'
        f'<span class="time">{time}</span>'
        f'<span class="text"><span class="title">{escape(clean(event.title))}</span>{desc}</span></li>'
    )


def render_html(events: list[Event], now: datetime, fonts_css: str = "",
                crest_src: str | None = None) -> str:
    rows = "\n".join(_row(e) for e in events) or \
        '    <li class="empty">Zurzeit keine Termine</li>'
    crest = f'<img src="{escape(crest_src)}" alt="">' if crest_src else ""
    stand = f"{WEEKDAYS[now.weekday()]} {now:%d.%m.%Y, %H:%M}"
    return PAGE.substitute(fonts_css=fonts_css, crest=crest, rows=rows, stand=stand)
