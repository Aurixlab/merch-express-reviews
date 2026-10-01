"""Fetches the Google reviews once and saves them as reviews.json.

Run weekly by .github/workflows/refresh.yml. The Merch Express website reads
reviews.json from GitHub Pages instead of calling Google on every page view,
so Google is asked once a week rather than thousands of times a month.

A bad or empty answer never overwrites the last good file: the script exits
non-zero, the commit step is skipped, and the site keeps the previous copy.
"""
import json, sys, urllib.request
from datetime import datetime, timezone

WORKER = "https://bp-google-reviews.aurixlab.workers.dev/?placeId=ChIJ70SmqDNwcVMRFMZLTL4wPJg"

with urllib.request.urlopen(urllib.request.Request(WORKER, headers={"User-Agent": "merch-express-reviews"}), timeout=30) as res:
    data = json.load(res)

result = data.get("result") or {}
if data.get("status") != "OK" or not isinstance(result.get("reviews"), list) or not result.get("rating"):
    sys.exit(f"Refusing to save: unexpected answer {json.dumps(data)[:300]}")

data["fetched_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
with open("reviews.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print(f"Saved: rating {result['rating']}, {result.get('user_ratings_total')} reviews, {len(result['reviews'])} review texts")
