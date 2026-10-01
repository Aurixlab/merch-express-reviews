# Merch Express Google reviews (weekly cache)

`reviews.json` holds Merch Express's Google rating, review count and latest
reviews. It is served from GitHub Pages:

https://aurixlab.github.io/merch-express-reviews/reviews.json

The merchexpresscanada.ca theme reads this file instead of calling the
Google Places API on every page view, which cost about CA$50/month in
September 2026. The GitHub Action in `.github/workflows/refresh.yml` refreshes
it every Monday (one Google lookup per week) and can be run by hand from the
Actions tab ("Refresh Google reviews" → Run workflow).

If a refresh fails, the previous `reviews.json` stays in place and the site
keeps working.

Full background (the September 2026 bill, what changed, costs, open items): see [CONTEXT.md](CONTEXT.md).
