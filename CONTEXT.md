# Why this repo exists

## The problem (September 2026)

The September 2026 Google Cloud bill was **CA$58.60**. Almost all of it came from one project:

| Project | Service | SKU | Cost |
|---|---|---|---|
| BudgetPromotion-Reviews | Places API | Atmosphere Data | $32.53 |
| BudgetPromotion-Reviews | Places API | Places Details | $16.33 |
| Default Gemini Project | — | — | $9.73 |

The Places API charges came from the **Google reviews on merchexpresscanada.ca**.

Every reviews section on the site asked a Cloudflare worker (`bp-google-reviews.aurixlab.workers.dev`) for Merch Express's rating, review count and latest reviews. The worker called the Google Places API to get them.

- **The call happened on every page view.** The browser code used `cache: 'no-store'`, and the worker sent no caching headers. That meant one paid Google request per visit.
- **Each request asks for rating, review count and reviews.** Google bills those fields as *Atmosphere Data* on top of *Places Details*, which is why the bill has two lines.
- **The cost scales with traffic.** At Google's list price, $32.53 of Atmosphere Data is roughly 6,500 paid lookups in one month.

The pages that made the call:

- the homepage (*Customer Experiences*, which also fills in the live review count),
- the About page,
- the T-shirts collection page,
- the cart page (Google reviews slider),
- every collection page, from **2026-09-27**, when *Customer Experiences* was added to them.

The Sep 27 change only affected the last few days of September. Most of the September cost came from the pages that already had reviews. The change would have pushed October higher; Google forecast $62.36.

## The fix (2026-10-02)

The website no longer calls Google when someone views a page.

1. **This repo holds a saved copy** of the reviews in [`reviews.json`](reviews.json), served by GitHub Pages:
   `https://aurixlab.github.io/merch-express-reviews/reviews.json`
   The file has the same format as the worker's response (`status`, `result.rating`, `result.user_ratings_total`, `result.reviews`), plus a `fetched_at` timestamp.
2. **A GitHub Action refreshes it once a week.** [`.github/workflows/refresh.yml`](.github/workflows/refresh.yml) runs every **Monday at 15:00 UTC**. It calls the worker once (one Google lookup) and commits the new file.
3. **The theme reads the saved copy.** The four places in the Shopify theme that used the worker now point to the GitHub Pages URL:
   - `assets/mx-home.js` (homepage, collection pages and About page carousel, plus the review count)
   - `sections/google-reviews.liquid` (cart page slider)
   - `sections/custom-apparel-reviews.liquid` (setting default)
   - `snippets/bp-about-google-reviews.liquid` (old About section, no longer on the page)

After the switch, browser checks of the homepage, a collection page, T-shirts, About and the cart all showed **zero calls to the worker**, and the reviews still displayed.

## Cost now

| | Before | After |
|---|---|---|
| Google lookups | One per page view (thousands per month) | One per week (about 4 per month) |
| Places API cost | About CA$50 per month | About CA$0.10 per month (effectively $0) |

The estimate for October 2026 was **about CA$13–20** in total:

- **Places API, about $3–9.** This is Oct 1–2 only, before the switch.
- **Gemini, about $10.** This project is unrelated to reviews; it is probably the quote form's follow-up emails.

## Running it

**Nothing needs to be done weekly.** The job runs by itself.

- **To refresh by hand:** go to GitHub → `Aurixlab/merch-express-reviews` → **Actions** → *Refresh Google reviews* → **Run workflow**.
- **If a refresh fails** (for example, Google or the worker is down), [`scripts/refresh.py`](scripts/refresh.py) refuses to save a bad answer. The previous `reviews.json` stays in place and the site keeps working.
- **If GitHub Pages is unreachable,** each theme section falls back to the reviews saved in the theme itself.
- **GitHub pauses scheduled jobs in repos with no activity for 60 days.** The weekly commit counts as activity, but if the job ever shows as disabled, re-enable it in the Actions tab.

## Still open

- **The worker is still public.** Anyone who calls `bp-google-reviews.aurixlab.workers.dev` directly still costs money. Set a daily quota on the Places API, about 50 requests per day, under Google Cloud → APIs & Services → Places API → Quotas. The weekly job needs 1.
- **A budget alert is recommended.** Under Google Cloud → Billing → Budgets & alerts, about $20 per month with alerts at 50 / 90 / 100%.
- **The worker's source code isn't in any Aurixlab repo.** It lives only in Cloudflare.
- **To confirm the fix:** go to Google Cloud → Billing → Reports, group by SKU, Oct 1 onward. *Atmosphere Data* and *Places Details* should drop to almost nothing from Oct 3.
