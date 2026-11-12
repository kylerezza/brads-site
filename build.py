#!/usr/bin/env python3
"""Builds the brads.io static site into docs/ (served by GitHub Pages).

Run:  python3 build.py
Edit the SETTINGS and APPS below, run it, commit docs/, push.
Standard library only.
"""
from __future__ import annotations

import html
import json
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------- settings
SITE_NAME = "brads.io"
DOMAIN = "brads.io"
# The legal person or company that publishes the apps (the App Store seller).
PUBLISHER = "Yucel Sanli"
# TODO(owner): make sure this address receives mail (email forwarding on the domain).
CONTACT_EMAIL = "support@brads.io"
EFFECTIVE_DATE = "November 11, 2026"
AD_PARTNER = "AppLovin"
AD_PARTNER_PRIVACY = "https://www.applovin.com/privacy/"
APPLE_EULA = "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"

# app-ads.txt (served at https://brads.io/app-ads.txt). Ad networks read it from the domain of the
# Marketing URL on the App Store page, so that URL must be https://brads.io/.
# TODO(owner): paste the exact line(s) from the AppLovin MAX dashboard (Account › app-ads.txt)
# here, e.g. "applovin.com, <your account ID>, DIRECT, <certification ID>". Copy them
# verbatim; do not type them by hand. Add one line per mediation network later.
APP_ADS_LINES: list[str] = []

# Only apps with published=True appear on the site. Turn an app on shortly
# before its App Store submission. This repo is public: never list an unreleased app here.
# photos: the app can turn a photo you pick into a puzzle, on the device.
# palette: 5-6 colours its scene on the wall is made from. store: App Store URL once live.
APPS = [
    {"slug": "stitchwell", "name": "Stitchwell", "what": "Cross stitch", "photos": True, "published": True,
     "one": "Cross stitch, one square at a time.",
     "more": "Real two-leg stitches on cream cloth. A new hoop every day, and a wall for everything you finish.",
     "hint": "Tap the cloth inside the hoop to lay a stitch.",
     "count": "You placed <b>0</b> stitches. The app has plenty more waiting.",
     "accent": "#9a3b48", "accent_dark": "#efa2ac",
     "palette": ["#b5525e", "#9a3b48", "#f1eadc", "#c9a27c", "#d5cbb8", "#2b2a28"],
     "finish": "finished pattern",
     "ads": ("a full-screen ad when you leave a finished pattern and one when you start a new pattern, "
             "a banner at the bottom of menu screens, and optional reward videos you choose to watch. "
             "There are never ads while you stitch."),
     "store": None},
]

# `python3 build.py --preview` builds into preview/ (gitignored) with placeholder apps,
# to see how the wall scales. Placeholders are fictional and never published.
PREVIEW = "--preview" in sys.argv
if PREVIEW:
    for n, pal in enumerate([["#3f6f8f", "#8fb3c9", "#e8eef2", "#25445a", "#c7d6df"],
                             ["#5c7d4e", "#a9c08f", "#eef0e2", "#34482c", "#d6dcc4"],
                             ["#b7793a", "#e3b778", "#f6ecdc", "#7a4a20", "#d9c3a3"],
                             ["#6d5a8f", "#b4a6cf", "#efeaf5", "#3f3357", "#d2c9e2"]], start=2):
        APPS.append({"slug": f"sample{n}", "name": f"Sample Craft {n}", "what": "Placeholder", "photos": False,
                     "published": True, "one": "A placeholder line, one thing at a time.",
                     "more": "This app is a stand-in to preview how the wall grows.", "hint": "Tap a tile to turn it.",
                     "count": "", "accent": pal[0], "accent_dark": pal[1], "palette": pal, "store": None})

ROOT = Path(__file__).resolve().parent
OUT = ROOT / ("preview" if PREVIEW else "docs")
STATIC = ROOT / "static"

e = html.escape


# ---------------------------------------------------------------- layout
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='7' fill='%23e4ddd0'/%3E%3Crect x='5' y='5' width='10' height='10' rx='2' fill='%232e2822'/%3E"
           "%3Crect x='17' y='5' width='10' height='10' rx='2' fill='%23efeae1'/%3E%3Crect x='5' y='17' width='10' height='10' rx='2' fill='%23efeae1'/%3E"
           "%3Crect x='17' y='17' width='10' height='10' rx='2' fill='%239a3b48'/%3E%3C/svg%3E")
DESCRIPTION = "brads makes small, calm games for iPhone and iPad, built on real crafts."


def page(title: str, body: str, depth: int, kind: str = "doc") -> str:
    up = "../" * depth
    home = kind == "home"
    script = f'<script src="{up}wall.js" defer></script>\n' if home else ""
    games = "#games" if home else f"{up}#games"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(DESCRIPTION)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(DESCRIPTION)}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#f7f4ee" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#151311" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="{up}style.css">
</head>
<body class="{'home-page' if home else 'doc-page'}">
<header class="site-head">
  <a class="wordmark" href="{up or './'}" aria-label="{e(SITE_NAME)} home">brads<i aria-hidden="true"></i></a>
  <nav aria-label="Main"><a href="{games}">Games</a><a href="{up}support/">Support</a><a href="{up}privacy/">Privacy</a></nav>
</header>
<main{'' if home else ' class="doc"'}>
{body}
</main>
<footer class="foot">
  <div class="foot-inner">
    <nav aria-label="Footer"><a href="{up}privacy/">Privacy</a><a href="{up}terms/">Terms</a><a href="{up}support/">Support</a><a href="mailto:{e(CONTACT_EMAIL)}">{e(CONTACT_EMAIL)}</a></nav>
    <p>&copy; 2026 {e(PUBLISHER)}. Small games, one tile at a time.</p>
  </div>
</footer>
{script}</body>
</html>
"""


def live_apps() -> list[dict]:
    return [a for a in APPS if a["published"]]


# ---------------------------------------------------------------- pages
def scene(n: int, a: dict) -> str:
    store = (f'<a class="pill" href="{e(a["store"])}">Get it on the App Store</a>' if a.get("store")
             else '<span class="pill">Coming soon to the App Store</span>')
    count = (f'<p class="scene-count" data-count-for="{e(a["slug"])}" hidden>{a["count"]}</p>' if a.get("count") else "")
    style = f'--accent:{a["accent"]}'
    return f"""
<article class="scene" id="{e(a['slug'])}" style="{style}">
  <div class="scene-wall">
    <canvas data-wall="scene" data-slug="{e(a['slug'])}" data-palette='{json.dumps(a["palette"])}'
      role="img" aria-label="{e(a['name'])}, shown on a wall of tiles"></canvas>
  </div>
  <div class="scene-panel">
    <p class="scene-no">No. {n:02d} &middot; {e(a['what'])}</p>
    <h3>{e(a['name'])}</h3>
    <p class="one">{e(a['one'])}</p>
    <p>{e(a['more'])}</p>
    <p class="free">Free on iPhone and iPad.</p>
    <div class="scene-links">{store}<a href="privacy/{e(a['slug'])}/">Privacy</a><a href="support/">Support</a></div>
    <p class="scene-hint">{e(a['hint'])}</p>
    {count}
  </div>
</article>"""


def home() -> str:
    apps = live_apps()
    scenes = "".join(scene(n, a) for n, a in enumerate(apps, start=1))
    palettes = json.dumps([a["palette"] for a in apps])
    accent_css = "".join(
        f'@media (prefers-color-scheme: dark) {{ #{a["slug"]} {{ --accent:{a["accent_dark"]} }} }}' for a in apps)
    return f"""
<style>{accent_css}</style>
<script type="application/json" id="palettes">{palettes}</script>
<section class="hero-wall" aria-label="The brads wordmark, built from tiles">
  <canvas data-wall="hero" role="img" aria-label="A wall of small wooden tiles that turn over to spell brads"></canvas>
</section>
<section class="hero-text">
  <h1>Games you can almost touch.</h1>
  <div>
    <p>brads makes small, calm games for iPhone and iPad, built on real crafts. Play a little each day. Nothing rushes you.</p>
    <p class="tap">Tap the wall.</p>
  </div>
</section>

<section class="games" id="games" aria-labelledby="games-title">
  <p class="label">The games</p>
  <h2 id="games-title">One craft, one game.</h2>
  {scenes}
</section>

<section class="frame" aria-labelledby="frame-title">
  <div class="frame-wall"><canvas data-wall="frame" role="img" aria-label="Plain tiles that have not turned yet"></canvas></div>
  <h2 id="frame-title">Still on the frame.</h2>
  <p>More crafts are being made. Each one becomes its own small game when it’s ready.</p>
</section>
"""


def privacy_body(app: dict | None) -> str:
    if app:
        heading = f"{e(app['name'])} privacy policy"
        scope = (f"This policy covers <strong>{e(app['name'])}</strong> for iPhone and iPad, "
                 f"published by {e(PUBLISHER)} (“we”).")
    else:
        heading = "Privacy policy"
        scope = (f"This policy covers every app published by {e(PUBLISHER)} (“we”) on the App Store "
                 f"(“our apps”). Each app also has its own page, listed at the bottom.")

    photos = ""
    if app is None or app["photos"]:
        who = "Some of our apps let" if app is None else "The app lets"
        photos = f"""
<h3>Photos you choose</h3>
<p>{who} you turn a photo into a puzzle. You pick the photo with Apple’s photo picker, so the app only
sees the photo you choose and never your whole library. The photo is processed on your device and is never
uploaded or shared with advertisers. Only the finished pattern is saved, on your device and, if you use iCloud,
in your own iCloud account.</p>
"""

    ads_where = ""
    if app and app.get("ads"):
        ads_where = f"<p><strong>Where ads appear in {e(app['name'])}:</strong> {e(app['ads'])}</p>\n"
    finish = app.get("finish", "finished game") if app else "finished game"

    per_app = ""
    if app is None and live_apps():
        per_app = "<h2>Policies per app</h2><ul>" + "".join(
            f'<li><a href="{a["slug"]}/">{e(a["name"])}</a></li>' for a in live_apps()
        ) + "</ul>"

    return f"""
<article class="doc">
<h1>{heading}</h1>
<p class="meta">Effective {e(EFFECTIVE_DATE)}</p>
<p>{scope}</p>

<div class="callout">
  <p><strong>The short version:</strong> our apps are free to play with ads. The ads are provided by
  {e(AD_PARTNER)}, which collects some device and usage data to show and measure ads. If you allow tracking,
  ads can be personalised; if you don’t, you still see ads, just not personalised ones. A one-time Remove Ads
  purchase turns off pop-up and banner ads, and a monthly subscription removes all ads. We do not run our own analytics, and we have no accounts.</p>
</div>

<h2>Data collected for advertising</h2>
{ads_where}<p>When you use the free version, the advertising software inside the app ({e(AD_PARTNER)}, including its
ad mediation partners) may collect:</p>
<ul>
  <li><strong>Device identifiers</strong> — the advertising identifier (IDFA) only if you allow tracking, and
  identifiers for this app on your device;</li>
  <li><strong>Device and network information</strong> — such as device model, operating system, language,
  IP address and the approximate location derived from it;</li>
  <li><strong>Ad interactions and app usage</strong> — such as which ads were shown or tapped and basic events
  needed to decide when ads are shown;</li>
  <li><strong>Diagnostics</strong> — such as ad-loading errors and performance data.</li>
</ul>
<p>This data is used to show ads, limit how often you see them, measure them, prevent fraud and, if you allow
tracking, personalise them. {e(AD_PARTNER)} processes it under its own privacy policy:
<a href="{AD_PARTNER_PRIVACY}">{e(AD_PARTNER_PRIVACY)}</a>. We receive only aggregated reports (for example,
how many ads were shown) and cannot identify you from them.</p>

<h3>Your choices</h3>
<ul>
  <li><strong>Tracking:</strong> after your first {e(finish)}, the app asks whether it may track you
  (Apple’s App Tracking Transparency prompt). You can change this any time in Settings › Privacy &amp; Security ›
  Tracking.</li>
  <li><strong>Personalised ads:</strong> if you decline tracking, ads are not personalised.</li>
  <li><strong>Fewer or no ads:</strong> the one-time Remove Ads purchase turns off pop-up and banner ads; an active monthly subscription turns off all ads.</li>
  <li><strong>Opt-out requests:</strong> you can ask {e(AD_PARTNER)} not to sell or share your data, or to
  delete data it holds, using the options in its privacy policy.</li>
</ul>

<h2>Data we do not collect</h2>
<p>We do not ask for your name, email or any account. We do not use separate analytics, attribution or
crash-reporting tools. We do not sell data ourselves.</p>

<h2>Where your game data lives</h2>
<h3>On your device</h3>
<p>Your progress, settings and creations are stored on your device.</p>
<h3>Your own iCloud (optional)</h3>
<p>If you are signed in to iCloud, the app can sync your progress between your devices using Apple’s iCloud
in your private iCloud account. We cannot see or access this data. You can turn this off and delete it in
Settings › [your name] › iCloud.</p>
{photos}
<h3>Purchases and subscriptions</h3>
<p>Purchases and subscriptions are handled entirely by Apple through the App Store. We never see your name,
email or payment details. The app only asks Apple whether a purchase or subscription is active. Manage or
cancel subscriptions in Settings › [your name] › Subscriptions.</p>
<h3>Game Center (optional)</h3>
<p>If you choose to use Game Center for achievements or leaderboards, Apple handles it under
<a href="https://www.apple.com/legal/privacy/">Apple’s Privacy Policy</a>. We only see what Apple shows to
all developers on a leaderboard, such as your Game Center nickname and score.</p>
<h3>Notifications</h3>
<p>Reminders are local notifications created on your device. They are off until you turn them on.</p>
<h3>Crash reports from Apple</h3>
<p>If you have chosen to share analytics with app developers in your device settings, Apple may give us
anonymous crash reports and usage statistics. Change this in Settings › Privacy &amp; Security ›
Analytics &amp; Improvements.</p>

<h2>Children</h2>
<p>Our apps are made for a general audience and are not directed at children under 13. We do not knowingly
collect personal data from children. If you believe a child has used one of our apps and data was collected,
contact us and we will help you ask {e(AD_PARTNER)} to delete it.</p>

<h2>Your rights</h2>
<p>Depending on where you live, you may have rights to access, delete or object to the use of personal data.
We do not hold personal data about you ourselves; advertising data is held by {e(AD_PARTNER)}, and you can use
its privacy options or write to us and we will help.</p>

<h2>Changes to this policy</h2>
<p>If this policy changes, we will update this page and the effective date above, and update the App Store
privacy label before the changed version is released.</p>

<h2>Contact</h2>
<p>{e(PUBLISHER)} &middot; <a href="mailto:{e(CONTACT_EMAIL)}">{e(CONTACT_EMAIL)}</a></p>
{per_app}
</article>
"""


def terms() -> str:
    return f"""
<article class="doc">
<h1>Terms of use</h1>
<p>Our apps are licensed to you under Apple’s standard
<a href="{APPLE_EULA}">Licensed Application End User License Agreement (EULA)</a>.
No separate terms apply.</p>
<p>Purchases and subscriptions are sold through the App Store and follow Apple’s
<a href="https://www.apple.com/legal/internet-services/itunes/">Media Services Terms and Conditions</a>.
Subscriptions renew automatically unless cancelled at least 24 hours before the end of the current period;
manage them in Settings › [your name] › Subscriptions.</p>
<p>How we handle data is described in our <a href="../privacy/">privacy policy</a>.</p>
</article>
"""


def support() -> str:
    return f"""
<article class="doc">
<h1>Support</h1>
<p>Questions, bugs or ideas? Email <a href="mailto:{e(CONTACT_EMAIL)}">{e(CONTACT_EMAIL)}</a>.
Tell us which app, your device and iOS version, and what happened.</p>

<h2>Common questions</h2>
<h3>How do I restore a purchase?</h3>
<p>Open the app’s Settings and tap <em>Restore Purchases</em>, signed in with the same Apple Account you bought with.</p>
<h3>How do I remove ads?</h3>
<p>Buy <em>Remove Ads</em> once in the app’s Settings to turn off pop-up and banner ads for good, or start the monthly subscription, which turns off all ads and unlocks everything while it is active.</p>
<h3>How do I cancel a subscription?</h3>
<p>On your iPhone or iPad: Settings › [your name] › Subscriptions, then choose the app.</p>
<h3>How do I get a refund?</h3>
<p>Refunds are handled by Apple at <a href="https://reportaproblem.apple.com">reportaproblem.apple.com</a>.</p>
<h3>My progress isn’t on my new device.</h3>
<p>Make sure both devices are signed in to the same iCloud account and that iCloud is on for the app
(Settings › [your name] › iCloud). Open the app on the old device once while online so it can sync.</p>
</article>
"""


def not_found() -> str:
    cells = "".join(f'<i class="{"off" if n == 17 else "on" if n in (0, 6, 12, 18, 24, 4, 8, 16, 20) else ""}"></i>' for n in range(25))
    return f"""
<div class="lost">
  <div class="tiles404" aria-hidden="true">{cells}</div>
  <h1>A tile fell off.</h1>
  <p>This page isn’t on the wall.</p>
  <p><a class="btn" href="/">Back to the wall</a></p>
</div>
"""


# ---------------------------------------------------------------- build
def write(rel: str, title: str, body: str, kind: str = "doc") -> None:
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    depth = rel.count("/")
    path.write_text(page(title, body, depth, kind), encoding="utf-8")


def write_app_ads() -> None:
    header = [f"# app-ads.txt for {DOMAIN} (apps published by {PUBLISHER}). See https://iabtechlab.com/ads-txt/"]
    if not APP_ADS_LINES:
        header.append("# TODO: add the AppLovin line from the MAX dashboard (APP_ADS_LINES in build.py).")
    (OUT / "app-ads.txt").write_text("\n".join(header + APP_ADS_LINES) + "\n", encoding="utf-8")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(STATIC / "style.css", OUT / "style.css")
    shutil.copy(STATIC / "wall.js", OUT / "wall.js")
    (OUT / "CNAME").write_text(DOMAIN + "\n")
    (OUT / ".nojekyll").write_text("")

    write("index.html", f"{SITE_NAME} · games you can almost touch", home(), "home")
    write("privacy/index.html", f"Privacy policy · {SITE_NAME}", privacy_body(None))
    for app in live_apps():
        write(f"privacy/{app['slug']}/index.html", f"{app['name']} privacy policy · {SITE_NAME}", privacy_body(app))
    write_app_ads()
    write("terms/index.html", f"Terms of use · {SITE_NAME}", terms())
    write("support/index.html", f"Support · {SITE_NAME}", support())
    (OUT / "404.html").write_text(
        page(f"Not found · {SITE_NAME}", not_found(), 0)
        .replace('href="style.css"', 'href="/style.css"').replace('href="./"', 'href="/"')
        .replace('href="support/"', 'href="/support/"').replace('href="privacy/"', 'href="/privacy/"')
        .replace('href="terms/"', 'href="/terms/"').replace('href="#games"', 'href="/#games"'),
        encoding="utf-8")
    print(f"Built {sum(1 for _ in OUT.rglob('*.html'))} pages into {OUT}")


if __name__ == "__main__":
    main()
