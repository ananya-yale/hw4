# Usability Improvements (Problem 9)

Log of usability improvements made, what was added, and why it helps a Campus Customs shopper or the business.

---

## Frontend #1: Icons on the home page feature sections

**What:** Added a small circular icon badge above each heading in the "Why Campus Customs" and "Find Your Fit" sections on the home page (people, shield, hoodie, sparkle, ruler, chat-bubble — [FeatureIcon.tsx](../frontend/src/components/FeatureIcon.tsx), wired into [HomePage.tsx](../frontend/src/pages/HomePage.tsx)). Plain inline SVGs, no new dependency, styled with a white circular badge and soft shadow so they read clearly on both the white and light-blue section backgrounds.

**Why it helps:** The six feature blocks were previously just a heading + a paragraph of text, which read as visually flat and text-heavy ("too sparse"). A small icon gives each block an immediate visual anchor, making the page easier to scan at a glance (shoppers skim before they read) and making the homepage feel more like a finished storefront than a placeholder page — first impressions matter for a shop's perceived trustworthiness.

---

## Frontend #2: Filter + sort on the Products page

**What:** Added a small toolbar above the product grid ([ProductsPage.tsx](../frontend/src/pages/ProductsPage.tsx)) with a **garment-type filter** and a **price sort** (Featured / Low to High / High to Low). Both options are derived from whatever set of products is currently showing — the full 102-item catalogue, or a narrower set of chat search results — so the filter list never shows irrelevant categories, and the toolbar works identically in both contexts. Switching data sets (e.g. clearing a chat search, or getting new chat results) resets the filter/sort so it can't silently hide a new result set.

**Why it helps:** With 102 items and (before this) zero way to narrow the full catalogue except through chat, a shopper who just wants to browse was stuck scrolling through everything or guessing a chat query. A type filter + price sort is the single highest-leverage, lowest-effort addition for anyone browsing normally — and because it also applies to chat search results, a shopper can ask the bot for "hoodies" and then further sort *that* set by price without typing another message. For the business: fewer abandoned browsing sessions from "I can't find what I want" friction.

---

## Backend/agent #1: Typo-tolerant product search

**What:** `search_products` ([backend/tools.py](../backend/tools.py)) now falls back to fuzzy matching (Python's `difflib`, cutoff 0.7) for any query word that doesn't find an exact substring hit, so misspellings like "hoody," "crewnek," or "sweatshit" still match "hoodie," "crewneck," "sweatshirt." Purely local string comparison — no extra LLM call, so it costs zero additional tokens per search.

**Why it helps:** Shoppers typing fast on a phone or just unsure of spelling ("sweatshert," "quarter zip") would previously get a flat "no matches" from the agent and might give up. Now a typo still surfaces the right products. For the business, this directly reduces dead-end searches that would otherwise look like "we don't carry that" when the item was there all along.

---

## Backend/agent #2: Low-stock urgency signal

**What:** `check_size_stock` now returns a `low_stock: bool` flag and phrases the message as "only N left!" once quantity drops to ≤5 for that size; `ProductCard` (used by `search_products`/`get_product_details`/chat cards) now includes a `low_stock_sizes` list computed the same way. Both are pure Python computed from the existing inventory numbers — no extra model call. [prompts/prompt.md](../backend/prompts/prompt.md) tells the agent it's fine to mention this casually (but not spam it) for urgency.

**Why it helps:** "Only 2 left in size M!" is a well-known, honest urgency cue that nudges a browsing shopper toward actually buying before the size disappears — all the numbers come straight from the same inventory table the stock pages already show, so it's never an invented claim. For the business, this is a free, zero-token conversion nudge sitting on data that already existed but wasn't being surfaced conversationally before.

### Verified behavior

- Filter/sort: tested on the full catalogue (filtering to "pullover hoodie" correctly narrowed 102→18 items; sorting by price correctly reordered all 102 by price ascending) and on chat search results (asking the chatbot "Show me fleece jackets" produced an 8-item result set, and the toolbar's type dropdown correctly only listed the garment types present in those 8 items).
- Typo search: `search_products("hoody")` and `search_products("crewnek")` both returned 8 real matches each (previously would've returned 0 for a non-substring typo). Verified through the full agent too, including a deliberately-misspelled live chat message.
- Low stock: `check_size_stock` on a real low-quantity row (2025 Yale Vs Harvard T-Shirt, size L, qty 2) returned `low_stock: true` and the message "only 2 left!"; verified end-to-end through the agent, which relayed the urgency naturally in a live reply.
