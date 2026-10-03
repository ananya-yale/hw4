# Design / Style Pass (Problem 10)

Concise log of the visual upgrades made to feel like a real storefront, and why each one should help customers stick around and buy.

---

## 1. Collegiate display font (Playfair Display)

**What:** All headings (nav brand, hero, section titles, product names/pages, auth forms) now use "Playfair Display," a bold serif, loaded via Google Fonts. Body text stays the original clean sans-serif. See [index.html](../frontend/index.html) and `--font-display` in [index.css](../frontend/src/index.css).

**Why it helps:** A generic system-font site reads as a template or a school project. A confident serif for headlines signals "established, trustworthy brand" (the same cue traditional university/Ivy League and heritage apparel brands lean on) without touching body readability. First impressions drive whether a visitor trusts a shop enough to enter card details later.

## 2. Gold accent + micro-interactions

**What:** Added a muted gold accent color (`--gold`/`--gold-dark`) used on button/link hovers, the nav "Create Account" pill, and feature icons. Added hover polish throughout: product cards lift and their image zooms slightly on hover, the hero button scales and gets a gold outline, a subtle page fade-in plays on navigation. See [App.css](../frontend/src/App.css) and [index.css](../frontend/src/index.css).

**Why it helps:** An all-navy-and-white site feels flat and corporate. A warm gold accent (classic trophy/varsity color) adds a premium touch without clashing with Yale blue. The hover/motion details make the site feel responsive and alive — small signals that someone is maintaining a real, polished product, which builds the confidence needed to complete a purchase.

## 3. "Selling Fast" badge on low-stock products

**What:** Product cards show an amber "Selling Fast" corner badge when a product's *total* stock across all sizes is low (≤25 units — tuned after checking the real data; see below). See [ProductCard.tsx](../frontend/src/components/ProductCard.tsx).

**Why it helps:** Scarcity cues are a well-established, honest way to nudge a browsing shopper toward deciding now instead of "I'll come back later" (and never doing so). For the business, this converts passive browsing into urgency using data that was already sitting in the database.

**A real mistake caught before shipping:** the badge was first wired to the same `low_stock_sizes` data the chat agent uses (any single size ≤5 units). That flagged **71 of 102 products (70%)** — checked the actual data and confirmed it wasn't a bug, just that per-size quantities are drawn from a range where "one of six sizes is low" is extremely common. A badge on 70% of products is worse than no badge at all — it stops meaning anything and starts looking untrustworthy ("everything is always almost sold out" reads as fake urgency). Switched the badge trigger to **total stock across all sizes**, checked the real distribution, and picked a threshold (≤25 units) that flags **8 of 102 products (~8%)** — rare enough to be a credible, genuine signal. The per-size `low_stock_sizes` data is still used as-is by the chat agent, where "only 2 left in size M" for a size the customer specifically asked about is accurate and useful regardless of overall stock.

---

### Verified behavior

Checked in the browser: all headings render in the new serif while body text is unchanged; hero button, nav CTA, product cards, and feature icons all show the gold-accented hover states; the Products grid shows the "Selling Fast" badge on a small, credible subset of cards (8 of 102) rather than most of them; no console errors.
