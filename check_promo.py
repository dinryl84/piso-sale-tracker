#!/usr/bin/env python3
"""
Piso Sale Tracker
------------------
Checks Google News for recent Cebu Pacific / AirAsia / PAL seat-sale
announcements, and pushes a free notification (via ntfy.sh) whenever a
new article shows up that we haven't flagged before.

Designed to run on a schedule via GitHub Actions (free tier).
State (which articles we've already seen) is kept in seen.json,
which the workflow commits back to the repo after each run.
"""

import json
import os
import re
import sys
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

STATE_FILE = Path(__file__).parent / "seen.json"

# Searches to run. Feel free to add/remove queries.
QUERIES = [
    "Cebu Pacific piso sale",
    "Cebu Pacific seat sale",
    "AirAsia Philippines seat sale",
    "Philippine Airlines seat sale promo",
]

# Only alert if the article title/snippet mentions one of these —
# keeps noise down to sale announcements specifically.
RELEVANT_KEYWORDS = [
    "piso sale", "seat sale", "sale fare", "promo fare", "p1 one-way",
    "php 1", "₱1 ", "seat fest",
]

NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "").strip()


def fetch_rss(query: str) -> str:
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({
        "q": query,
        "hl": "en-PH",
        "gl": "PH",
        "ceid": "PH:en",
    })
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_items(xml_text: str):
    root = ET.fromstring(xml_text)
    items = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        items.append({"title": title, "link": link, "pubDate": pub_date})
    return items


def is_relevant(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in RELEVANT_KEYWORDS)


def load_seen() -> set:
    if STATE_FILE.exists():
        try:
            return set(json.loads(STATE_FILE.read_text()))
        except Exception:
            return set()
    return set()


def save_seen(seen: set):
    # Keep the file from growing forever — cap at the most recent 500 links.
    trimmed = list(seen)[-500:]
    STATE_FILE.write_text(json.dumps(trimmed, indent=2))


def notify(title: str, link: str):
    if not NTFY_TOPIC:
        print(f"[no NTFY_TOPIC set] Would have notified: {title}\n{link}")
        return
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    data = link.encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Title": "Flight Sale Alert",
        "Tags": "airplane,moneybag",
        "Content-Type": "text/plain; charset=utf-8",
        "X-Message": title[:200].encode("ascii", "ignore").decode(),
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"Notified ({resp.status}): {title}")
    except Exception as e:
        print(f"Failed to notify: {e}", file=sys.stderr)


def main():
    seen = load_seen()
    new_seen = set(seen)
    found_new = False

    for q in QUERIES:
        try:
            xml_text = fetch_rss(q)
            items = parse_items(xml_text)
        except Exception as e:
            print(f"Error fetching '{q}': {e}", file=sys.stderr)
            continue

        for item in items:
            link = item["link"]
            title = item["title"]
            if link in seen:
                continue
            if not is_relevant(title):
                continue
            found_new = True
            notify(title, link)
            new_seen.add(link)

    save_seen(new_seen)
    if not found_new:
        print("No new relevant sale articles found this run.")


if __name__ == "__main__":
    main()
