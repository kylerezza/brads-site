#!/usr/bin/env python3
"""Builds the brads.io static site into docs/ (served by GitHub Pages).

Run:  python3 build.py
Edit the SETTINGS and APPS below, run it, commit docs/, push.
Standard library only.
"""
from __future__ import annotations

import html
import random
import shutil
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

# Only apps with published=True appear on the site. Turn an app on shortly
# before its App Store submission so unreleased names stay private.
# photos: the app can turn a photo you pick into a puzzle, on the device.
APPS = [
    {"slug": "stitchwell", "name": "Stitchwell", "what": "Cross stitch game", "photos": True, "published": True},
    # Add each app here shortly before its App Store submission, e.g.:
    # {"slug": "rulesweeper", "name": "Rulesweeper", "what": "Minesweeper with rule twists", "photos": False, "published": True},
    # This repo is public (GitHub Pages), so do not list unreleased apps early.
]

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"
STATIC = ROOT / "static"

e = html.escape


# ---------------------------------------------------------------- layout
X_MARK = ('<svg viewBox="0 0 10 10" aria-hidden="true"><path d="M2 8 8 2M2 2l6 6" stroke="currentColor" '
          'stroke-width="2.6" stroke-linecap="round" fill="none"/></svg>')
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='8' fill='%23f1eadc'/%3E%3Cpath d='M9 23 23 9M9 9l14 14' "
           "stroke='%239a3b48' stroke-width='5' stroke-linecap='round'/%3E%3C/svg%3E")
DESCRIPTION = "Small, calm games for iPhone and iPad, made by hand by one person."


def back_of_work() -> str:
    """The footer shows the reverse of the fabric: loose tails, carried threads and knots. Deterministic."""
    rnd = random.Random(7)
    floss = ["#9a3b48", "#74293a", "#c06272", "#6a7f6e", "#c9a27c", "#8a5f86"]
    parts = []
    for _ in range(9):  # long carried threads
        y1, y2 = rnd.uniform(20, 200), rnd.uniform(20, 200)
        x1 = rnd.uniform(-60, 500); x2 = x1 + rnd.uniform(300, 800)
        cy = (y1 + y2) / 2 + rnd.uniform(-40, 40)
        parts.append(f'<path d="M{x1:.0f} {y1:.0f}Q{(x1+x2)/2:.0f} {cy:.0f} {x2:.0f} {y2:.0f}" stroke="{rnd.choice(floss)}" '
                     f'stroke-width="{rnd.uniform(1.5, 2.6):.1f}" fill="none" stroke-linecap="round" opacity="{rnd.uniform(0.35, 0.7):.2f}"/>')
    for _ in range(16):  # loose tails ending in knots
        x, y = rnd.uniform(0, 1200), rnd.uniform(10, 210)
        dx, dy = rnd.uniform(-90, 90), rnd.uniform(-50, 50)
        col = rnd.choice(floss)
        parts.append(f'<path d="M{x:.0f} {y:.0f}c{dx*0.3:.0f} {-abs(dy):.0f} {dx*0.8:.0f} {dy:.0f} {dx:.0f} {dy*0.6:.0f}" stroke="{col}" '
                     f'stroke-width="2" fill="none" stroke-linecap="round" opacity="0.65"/>'
                     f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(3, 5.5):.1f}" fill="{col}" opacity="0.75"/>')
    return ('<svg class="back-art" viewBox="0 0 1200 220" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">'
            + "".join(parts) + "</svg>")


BACK_ART = ""


def page(title: str, body: str, depth: int, kind: str = "doc") -> str:
    up = "../" * depth
    home = kind == "home"
    js_flag = '<script>document.documentElement.classList.add("js")</script>\n' if home else ""
    script = f'<script src="{up}home.js" defer></script>\n' if home else ""
    stitch_link = "#stitchwell" if home else f"{up}#stitchwell"
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
<meta name="theme-color" content="#f1eadc" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#2b2a28" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="{up}style.css">
{js_flag}</head>
<body class="{'home-page' if home else 'doc-page'}">
<header class="site-head">
  <a class="wordmark" href="{up or './'}" aria-label="{e(SITE_NAME)} home">brads{X_MARK}</a>
  <nav aria-label="Main"><a href="{stitch_link}">Stitchwell</a><a href="{up}support/">Support</a><a href="{up}privacy/">Privacy</a></nav>
</header>
<main{'' if home else ' class="doc"'}>
{body}
</main>
<footer class="back">
  {BACK_ART}
  <div class="back-inner">
    <p class="back-label">The back of the work.</p>
    <nav aria-label="Footer"><a href="{up}privacy/">Privacy</a><a href="{up}terms/">Terms</a><a href="{up}support/">Support</a><a href="mailto:{e(CONTACT_EMAIL)}">{e(CONTACT_EMAIL)}</a></nav>
    <p class="sign">Stitched in 2026 by {e(PUBLISHER)}.</p>
  </div>
</footer>
{script}</body>
</html>
"""


def live_apps() -> list[dict]:
    return [a for a in APPS if a["published"]]


# ---------------------------------------------------------------- pages
def home() -> str:
    tick = '<svg viewBox="0 0 10 10" aria-hidden="true"><path d="M2 8 8 2M2 2l6 6" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" fill="none"/></svg>'
    facts = [
        "Real two-leg X stitches, the \\ laid over the /, the way stitchers do it.",
        "Every finished piece goes in a hoop on your Wall.",
        "Real art, never AI.",
        "Turn a photo of your own into a pattern, right on your iPhone.",
        "Your progress syncs through your own iCloud.",
    ]
    fact_items = "".join(f"<li>{tick}<span>{e(f)}</span></li>" for f in facts)
    seam = '<div class="seam-wrap"><div class="seam sew" role="presentation"></div></div>'
    return f"""
<section class="hero" aria-labelledby="hero-title">
  <div class="hero-inner">
    <div class="hero-copy">
      <h1 id="hero-title">Small games, <em>made by hand.</em></h1>
      <p>One person. A few crafts. Done slowly and done well.</p>
      <p>Every game starts with something you can almost touch: thread, cloth, a quiet grid. Play a little each day. Nothing rushes you.</p>
      <p class="free">Free to play on iPhone and iPad.</p>
    </div>
    <div class="hoop-wrap" data-hoop>
      <div class="screw-tab" aria-hidden="true"></div><div class="screw" aria-hidden="true"></div>
      <div class="hoop"><div class="cloth">
        <canvas role="img" aria-label="A cross-stitched heart in an embroidery hoop. Move across it to add stitches."></canvas>
        <div class="sheen" aria-hidden="true"></div>
      </div></div>
      <p class="hint" aria-hidden="true"></p>
      <div class="hoop-bar no-js-hide">
        <p class="hoop-status"><b data-count>0</b> of <span data-total>0</span> stitches &middot; <b data-mine>0</b> by you</p>
        <p class="done-line" role="status">Finished.</p>
        <button class="btn quiet" id="finish" type="button">Finish it</button>
        <button class="btn quiet" id="again" type="button">Stitch again</button>
      </div>
    </div>
  </div>
</section>

<section class="section" id="stitchwell" aria-labelledby="sw-title">
  <div class="app">
    <div>
      <p class="eyebrow">Our first craft</p>
      <h2 id="sw-title">Stitchwell</h2>
      <p class="lede">Cross stitch, one square at a time. Tap or drag to lay stitches on cream cloth and watch a picture appear.</p>
      <ul class="facts">{fact_items}</ul>
      <div class="app-links"><span class="status-pill">Coming soon to the App Store</span><a href="privacy/stitchwell/">Stitchwell privacy</a></div>
    </div>
    <div class="studio needs-js" data-studio>
      <div class="studio-frame">
        <canvas role="img" aria-label="The picture, stitched as a cross-stitch pattern"></canvas>
        <div class="drop" aria-hidden="true">Drop a photo to stitch it</div>
      </div>
      <div class="studio-controls">
        <div class="studio-row">
          <label class="btn file-btn">Stitch your own photo<input type="file" accept="image/*"></label>
          <button class="btn quiet" type="button" data-save>Save image</button>
        </div>
        <label class="range">Stitches across <input type="range" min="24" max="72" step="4" value="44"><output>44 × 33</output></label>
        <ul class="swatches" aria-label="Floss colours in this pattern"></ul>
        <p class="fine">This runs in your browser. Your photo isn’t uploaded anywhere.</p>
      </div>
    </div>
  </div>
</section>

{seam}

<section class="section center" aria-labelledby="wt-title">
  <p class="eyebrow">On the worktable</p>
  <h2 id="wt-title">More crafts are being made.</h2>
  <p class="lede">Each one becomes its own small game when it’s ready.</p>
  <div class="table" aria-hidden="true"><div class="mini-hoop"><span></span></div><div class="mini-hoop"><span></span></div><div class="mini-hoop"><span></span></div></div>
  <p class="table-note">Not ready yet. Worth the wait.</p>
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
<p>When you use the free version, the advertising software inside the app ({e(AD_PARTNER)}, including its
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
  <li><strong>Tracking:</strong> after your first finished game, the app asks whether it may track you
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
    return """
<div class="lost">
  <svg viewBox="0 0 360 160" aria-hidden="true" focusable="false">
    <path d="M10 40 C 80 10, 120 90, 180 60 S 280 20, 300 110 S 340 150, 352 128" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-dasharray="14 7"/>
    <g stroke="currentColor" stroke-width="7" stroke-linecap="round" opacity="0.9"><path d="M60 120 80 100M60 100l20 20"/><path d="M96 130 116 110"/></g>
  </svg>
  <h1>A dropped stitch.</h1>
  <p>This page came loose from the cloth.</p>
  <p><a class="btn" href="/">Back to the hoop</a></p>
</div>
"""


# ---------------------------------------------------------------- build
def write(rel: str, title: str, body: str, kind: str = "doc") -> None:
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    depth = rel.count("/")
    path.write_text(page(title, body, depth, kind), encoding="utf-8")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    global BACK_ART
    BACK_ART = back_of_work()
    shutil.copy(STATIC / "style.css", OUT / "style.css")
    shutil.copy(STATIC / "home.js", OUT / "home.js")
    (OUT / "CNAME").write_text(DOMAIN + "\n")
    (OUT / ".nojekyll").write_text("")

    write("index.html", f"{SITE_NAME} · small games, made by hand", home(), "home")
    write("privacy/index.html", f"Privacy policy · {SITE_NAME}", privacy_body(None))
    for app in live_apps():
        write(f"privacy/{app['slug']}/index.html", f"{app['name']} privacy policy · {SITE_NAME}", privacy_body(app))
    write("terms/index.html", f"Terms of use · {SITE_NAME}", terms())
    write("support/index.html", f"Support · {SITE_NAME}", support())
    (OUT / "404.html").write_text(
        page(f"Not found · {SITE_NAME}", not_found(), 0)
        .replace('href="style.css"', 'href="/style.css"').replace('href="./"', 'href="/"')
        .replace('href="support/"', 'href="/support/"').replace('href="privacy/"', 'href="/privacy/"')
        .replace('href="terms/"', 'href="/terms/"').replace('href="#stitchwell"', 'href="/#stitchwell"'),
        encoding="utf-8")
    print(f"Built {sum(1 for _ in OUT.rglob('*.html'))} pages into {OUT}")


if __name__ == "__main__":
    main()
