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

## app-ads.txt (ads)

`build.py` writes `docs/app-ads.txt`, served at `https://brads.io/app-ads.txt`. Ad networks check it to confirm that ads in our apps are sold by us.

1. In the AppLovin MAX dashboard, open Account › app-ads.txt and copy the line(s) exactly.
2. Paste each line as a string into `APP_ADS_LINES` at the top of `build.py`, run `python3 build.py`, commit, push.
3. In App Store Connect, set each app's **Marketing URL** to `https://brads.io/` (networks look for the file on that domain; verify in AppLovin's docs).
4. Check `https://brads.io/app-ads.txt` in a browser. AppLovin shows "verified" after its next crawl (can take a day or more).

Until step 2 the file holds only comments, which is valid and harmless.

## One-time setup (owner)

### 1. Publish on GitHub Pages
1. Create a **public** GitHub repo `brads-site` and push this folder (`gh repo create brads-site --public --source . --push`).
2. On GitHub: repo › Settings › Pages › Build and deployment › Source **Deploy from a branch** › Branch `main`, folder `/docs` › Save.
3. In the same page, Custom domain should show `brads.io` (it comes from `docs/CNAME`).

### 2. Point brads.io at GitHub (WordPress.com › Upgrades › Domains › brads.io)
**First, name servers.** The domain is registered at WordPress.com but (as of 2026-11-11) its name servers are still `ns1/ns2.sedoparking.com`, so it shows a parking page and any DNS records added at WordPress.com are ignored. In **Name servers**, switch to **Use WordPress.com name servers** (`ns1.wordpress.com`, `ns2.wordpress.com`, `ns3.wordpress.com`). If the domain is listed for sale or parked in a Sedo account, remove it there too.

Then, in **DNS records**: Remove any existing **A**/**AAAA** records for the root (`@`) and any `www` record that points to WordPress, then add:

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
| CNAME | www | `kylerezza.github.io` |

If WordPress.com won't let you edit root records, the domain is probably still connected to a WordPress.com site; disconnect it from that site first (verify in WordPress.com's domain settings).

### 3. Turn on HTTPS
After DNS has spread (minutes to a few hours), go back to GitHub › Settings › Pages, wait for the domain check to pass, and tick **Enforce HTTPS**.

### 4. Make the support address work
`support@brads.io` is printed on every page. In WordPress.com › Domains › brads.io › Email, set up **email forwarding** for `support@` to your inbox (verify it's free on your plan).

### 5. Check it
`dig +short NS brads.io` shows `wordpress.com` servers, `dig +short brads.io` shows the four `185.199.x.153` addresses, and `https://brads.io/privacy/stitchwell/` loads the Stitchwell policy.
