# Piso Sale Tracker (100% free)

Checks Google News once a day for new Cebu Pacific / AirAsia / PAL seat-sale
announcements and pushes a free notification to your phone the moment one
appears. No servers, no paid tiers.

## What it uses (all free)
- **GitHub Actions** — runs the check daily on GitHub's free tier (2,000 free
  minutes/month for private repos, unlimited for public repos; this job uses
  well under a minute per run).
- **ntfy.sh** — a free, no-signup push notification service. You pick a
  "topic" name and subscribe to it in their app; anything posted to that
  topic pops up as a phone notification.

## Setup (10 minutes)

### 1. Create the repo
- Create a free GitHub account if you don't have one: https://github.com/signup
- Create a new repository (public or private, either works) — e.g. `piso-sale-tracker`.
- Upload these three files/folders into it, keeping the folder structure:
  - `check_promo.py`
  - `seen.json`
  - `.github/workflows/check.yml`
  - `README.md` (optional, just for reference)

### 2. Set up ntfy.sh notifications
- Install the ntfy app: [Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy) or [iOS](https://apps.apple.com/us/app/ntfy/id1625396347)
- In the app, tap "Subscribe to topic" and make up a unique, hard-to-guess
  topic name (e.g. `dinryl-piso-sale-8f2k`) — anyone who knows the exact name
  could send to it too, so keep it non-obvious. No account needed.

### 3. Connect the topic to GitHub
- In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**
- Name: `NTFY_TOPIC`
- Value: the topic name you picked (e.g. `dinryl-piso-sale-8f2k`)

### 4. Enable the workflow
- Go to the **Actions** tab in your repo → you should see "Check Piso Sale".
- Click it, then **Enable workflow** if prompted.
- Click **Run workflow** once to test it manually — you should get a
  notification within a minute if there's a matching sale article, or just
  see "No new relevant sale articles found" in the log if not.

That's it — from here it runs automatically every day at 9 AM Philippine
time, and you'll get a push notification the moment a new piso/seat sale is
announced.

## Customizing
- **Search terms**: edit `QUERIES` in `check_promo.py` to track other routes
  or airlines.
- **Relevance filter**: edit `RELEVANT_KEYWORDS` to loosen/tighten what
  counts as a "sale" article.
- **Schedule**: edit the `cron` line in `.github/workflows/check.yml`
  (currently daily at 01:00 UTC / 09:00 PHT).
