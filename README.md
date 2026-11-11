# brads-site

The brads.io website: privacy policy (studio-wide and per app), terms (Apple's Standard EULA) and support.
Plain static HTML, built by one Python script, served free by GitHub Pages.

## Edit and rebuild

1. Change the settings or the `APPS` list at the top of `build.py`.
2. Run `python3 build.py`. This rewrites `docs/`.
3. Commit and push. GitHub Pages republishes in about a minute.

Add an app to `APPS` shortly before its App Store submission. The repo is public, so unreleased apps stay out of it.

## URLs for App Store Connect

| Field | Value |
|---|---|
| Privacy Policy URL | `https://brads.io/privacy/<app>/` (e.g. `https://brads.io/privacy/stitchwell/`) |
| Support URL | `https://brads.io/support/` |
| Marketing URL (optional) | `https://brads.io/` |
| License Agreement | Apple's Standard EULA (the default; nothing to upload) |

## One-time setup (owner)

### 1. Publish on GitHub Pages
1. Create a **public** GitHub repo `brads-site` and push this folder (`gh repo create brads-site --public --source . --push`).
2. On GitHub: repo › Settings › Pages › Build and deployment › Source **Deploy from a branch** › Branch `main`, folder `/docs` › Save.
3. In the same page, Custom domain should show `brads.io` (it comes from `docs/CNAME`).

### 2. Point brads.io at GitHub (WordPress.com › Upgrades › Domains › brads.io › DNS records)
Keep WordPress.com's name servers. Remove any existing **A**/**AAAA** records for the root (`@`) and any `www` record that points to WordPress, then add:

| Type | Name | Value |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| AAAA | @ | 2606:50c0:8000::153 |
| AAAA | @ | 2606:50c0:8001::153 |
| AAAA | @ | 2606:50c0:8002::153 |
| AAAA | @ | 2606:50c0:8003::153 |
| CNAME | www | `<your-github-username>.github.io` |

If WordPress.com won't let you edit root records, the domain is probably still connected to a WordPress.com site; disconnect it from that site first (verify in WordPress.com's domain settings).

### 3. Turn on HTTPS
After DNS has spread (minutes to a few hours), go back to GitHub › Settings › Pages, wait for the domain check to pass, and tick **Enforce HTTPS**.

### 4. Make the support address work
`support@brads.io` is printed on every page. In WordPress.com › Domains › brads.io › Email, set up **email forwarding** for `support@` to your inbox (verify it's free on your plan).

### 5. Fill in the publisher name
In `build.py`, set `PUBLISHER` to the exact legal name that Apple shows as the seller, then rebuild and push.
