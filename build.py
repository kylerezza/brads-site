#!/usr/bin/env python3
"""Builds the brads.io static site into docs/ (served by GitHub Pages).

Run:  python3 build.py
Edit the SETTINGS and APPS below, run it, commit docs/, push.
Standard library only.
"""
from __future__ import annotations

import html
import shutil
from pathlib import Path

# ---------------------------------------------------------------- settings
SITE_NAME = "brads.io"
DOMAIN = "brads.io"
# The legal person or company that publishes the apps (the App Store seller).
# TODO(owner): replace with the exact legal name once Apple enrolment is done.
PUBLISHER = "brads.io"
# TODO(owner): make sure this address receives mail (email forwarding on the domain).
CONTACT_EMAIL = "support@brads.io"
EFFECTIVE_DATE = "November 11, 2026"
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
def page(title: str, body: str, depth: int) -> str:
    up = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(SITE_NAME)}: small, calm games for iPhone and iPad.">
<link rel="stylesheet" href="{up}style.css">
</head>
<body>
<header class="site">
  <a class="brand" href="{up}">{e(SITE_NAME)}</a>
  <nav><a href="{up}privacy/">Privacy</a><a href="{up}terms/">Terms</a><a href="{up}support/">Support</a></nav>
</header>
<main>
{body}
</main>
<footer class="site">
  <p>&copy; 2026 {e(PUBLISHER)} &middot; <a href="mailto:{e(CONTACT_EMAIL)}">{e(CONTACT_EMAIL)}</a></p>
</footer>
</body>
</html>
"""


def live_apps() -> list[dict]:
    return [a for a in APPS if a["published"]]


# ---------------------------------------------------------------- pages
def home() -> str:
    items = "".join(
        f'<li><a href="privacy/{a["slug"]}/"><strong>{e(a["name"])}</strong></a>'
        f'<span>{e(a["what"])}</span></li>'
        for a in live_apps()
    )
    return f"""
<section class="hero">
  <h1>Small, calm games for iPhone and iPad.</h1>
  <p class="lead">No ads. No tracking. Your progress stays on your device and in your own iCloud.</p>
</section>
<section>
  <h2>Our apps</h2>
  <ul class="apps">{items}</ul>
</section>
"""


def privacy_body(app: dict | None) -> str:
    if app:
        heading = f"{e(app['name'])} privacy policy"
        scope = (f"This policy covers <strong>{e(app['name'])}</strong> for iPhone and iPad, "
                 f"published by {e(PUBLISHER)}.")
    else:
        heading = "Privacy policy"
        scope = (f"This policy covers every app published by {e(PUBLISHER)} on the App Store "
                 f"(“our apps”). Each app also has its own page, listed at the bottom.")

    photos = ""
    if app is None or app["photos"]:
        who = "Some of our apps let" if app is None else "The app lets"
        photos = f"""
<h3>Photos you choose</h3>
<p>{who} you turn a photo into a puzzle. You pick the photo with Apple’s photo picker, so the app only
sees the photo you choose and never your whole library. The photo is processed on your device and is never
uploaded. Only the finished pattern is saved, on your device and, if you use iCloud, in your own iCloud account.</p>
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
  <p><strong>The short version:</strong> we do not collect any data about you. No accounts, no ads, no analytics,
  no tracking. Your App Store privacy label says <strong>“Data Not Collected”</strong>.</p>
</div>

<h2>What we collect</h2>
<p>Nothing. Our apps do not send personal information, usage data, identifiers or diagnostics to us or to
anyone else. We do not use advertising, analytics, crash-reporting or tracking tools, and we do not sell or share data.</p>

<h2>Where your game data lives</h2>
<h3>On your device</h3>
<p>Your progress, settings and creations are stored on your device.</p>
<h3>Your own iCloud (optional)</h3>
<p>If you are signed in to iCloud, the app can sync your progress between your devices using Apple’s iCloud
in your private iCloud account. We cannot see or access this data. You can turn this off in your device’s
Settings › [your name] › iCloud, and delete it there.</p>
{photos}
<h3>Purchases and subscriptions</h3>
<p>Purchases and subscriptions are handled entirely by Apple through the App Store. We never see your name,
email or payment details. The app only asks Apple whether a purchase is active. You can manage or cancel
subscriptions in Settings › [your name] › Subscriptions.</p>
<h3>Game Center (optional)</h3>
<p>If you choose to use Game Center for achievements or leaderboards, Apple handles it under
<a href="https://www.apple.com/legal/privacy/">Apple’s Privacy Policy</a>. We only see what Apple shows to
all developers on a leaderboard, such as your Game Center nickname and score.</p>
<h3>Notifications</h3>
<p>Reminders are local notifications created on your device. They are off until you turn them on.</p>
<h3>Crash reports from Apple</h3>
<p>If you have chosen to share analytics with app developers in your device settings, Apple may give us
anonymous crash reports and usage statistics. You can change this in Settings › Privacy &amp; Security ›
Analytics &amp; Improvements.</p>

<h2>Children</h2>
<p>Our apps are made for a general audience and are not directed at children under 13. Because we collect no
data, we do not knowingly collect data from children.</p>

<h2>Your rights</h2>
<p>Because we hold no personal data about you, there is nothing for us to access, correct, export or delete.
Data in your iCloud account is under your control. If you have a question, write to us and we will answer.</p>

<h2>Changes to this policy</h2>
<p>If this policy changes, we will update this page and the effective date above. If an app ever starts
collecting data, we will update this policy and the App Store privacy label before that version is released.</p>

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
    return '<article class="doc"><h1>Page not found</h1><p><a href="/">Go to the home page</a>.</p></article>'


# ---------------------------------------------------------------- build
def write(rel: str, title: str, body: str) -> None:
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    depth = rel.count("/")
    path.write_text(page(title, body, depth), encoding="utf-8")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(STATIC / "style.css", OUT / "style.css")
    (OUT / "CNAME").write_text(DOMAIN + "\n")
    (OUT / ".nojekyll").write_text("")

    write("index.html", SITE_NAME, home())
    write("privacy/index.html", f"Privacy policy · {SITE_NAME}", privacy_body(None))
    for app in live_apps():
        write(f"privacy/{app['slug']}/index.html", f"{app['name']} privacy policy · {SITE_NAME}", privacy_body(app))
    write("terms/index.html", f"Terms of use · {SITE_NAME}", terms())
    write("support/index.html", f"Support · {SITE_NAME}", support())
    (OUT / "404.html").write_text(page(f"Not found · {SITE_NAME}", not_found(), 0).replace('href="style.css"', 'href="/style.css"'), encoding="utf-8")
    print(f"Built {sum(1 for _ in OUT.rglob('*.html'))} pages into {OUT}")


if __name__ == "__main__":
    main()
