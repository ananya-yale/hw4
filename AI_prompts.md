# AI Prompts Log

This file logs every prompt given to the AI assistant while working on Homework 4, organized by problem number (1-13). Follow-up prompts are logged under the same problem, with a note explaining why the follow-up was needed.

---

## Problem 1: Vibe coder prompts

**Prompt 1:**
> we're going to work in folder homework 4 today, put everything we do in there

**Prompt 2:**
> make a virtual environment because we're going to do python stuff and i think we need one

**Prompt 3:**
> we need an AI_prompts.md where we're going to log all the prompts i give you. if we need follow up prompts, log those too and why we needed a follow up. number it problems 1-13 and keep logging everything as we go.

**Prompt 4 (follow-up):**
> this was problem 1, it was called "Vibe coder prompts" (also log title of questions as we go)
>
> *Why follow-up:* Needed to retroactively attach the problem title to Problem 1 and label it, since the title wasn't given until after the prompts were already logged under a generic "Setup" heading.

## Problem 2: Analyze the database

**Prompt 1:**
> ok now problem 2 is called "Analyze the database." look at data/campus_customs.db and give me an overview of the fields of each table. make sure you include catalogue, inventory, and users bc those are most important but anything else that seems important stick in there too.
>
> ultimately we're going to make a shop and chatbot for campus customs so right now, we need to understand the lay of the land. make an output/harness.md and document each table, its fields, and a short line on why each field matters for our shop/chatbot.

*Note:* the database was actually located at `data/data/campus_customs.db` (one level deeper than the path given), so that's the path used in [output/harness.md](output/harness.md). Documented `catalogue`, `inventory`, `users`, and also included `chat_messages` since it captures the expected chatbot response shape (products bundled with per-size inventory), which is directly relevant to building the chatbot.

## Problem 3

**Prompt 1 (standing instruction, not tied to a specific problem):**
> also i forgot to say this earlier but when we start making calls to LLMs, i want you to use open ai 5.6 luna when possible but upgrade to terra when it would be more efficient to do so (don't burn all my tokens for dumb stuff but if luna would be slow / less efficient, switch up to terra)
>
> also use my PORTKEY_API_KEY when i need it (find my .env file and you'll see it) and obv never ever ever ever put my api key somewhere where other people could see it (this is going to be graded by outside people). got it?

*Action taken:* Found the `.env` file at `../.env` (one level up, in the `AI Foundations` folder) containing `PORTKEY_API_KEY`. Attempting to copy it into this folder was auto-blocked as a credential-leakage risk, so instead code in this project will load it directly from `../.env` via `python-dotenv` without ever duplicating/printing the key. Added [.gitignore](.gitignore) (excludes `.env`, `venv/`) and [.env.example](.env.example) (placeholder only) so the real key never risks being exposed to graders.

*(prompts for Problem 3 itself go here once given)*

## Problem 3: Build the campus customs website

**Prompt 1:**
> problem 3 is called "Build the campus customs website."
>
> front end: React + Vite + Typescript. nav bar at the top that includes links to main pages - home, products, about us, log in, and create account.
>
> for home and about us, it should take us to pages that use campus customs style wording (https://yalebulldogblue.com/ for reference) - but use your own words, don't just copy what's on the existing website.
>
> products page should show images from our catalogue (use image paths from out database) with basic product info (name, price, short description).
>
> you should be able to click a card on products and it should open a single-item page (large image on one side, full product text on the other. text should include description, price, sizes/stock).
>
> add a chat interface in the bottom right of the site. we'll sort out the agent and backend part of this in a future problem. for now, let's do a simple FastAPI app in backend/main.py to serve the product images - we'll grow this into an agent backend in a future problem.

*What was built:*
- `backend/main.py` — FastAPI app. Since the frontend needed actual product data (not just images) to render the products/detail pages, extended beyond "serve images" to also add `GET /api/products` and `GET /api/products/{product_id}` endpoints that join `catalogue` + `inventory` from the SQLite db — this seemed like the obvious minimal extension needed to make the page work, without yet building any agent/LLM logic (that's for a future problem). Also mounted `/media/products` as static files for the catalogue images.
- `frontend/` — Vite + React + TypeScript app with React Router. Pages: Home, About (original Campus Customs copy, tone-matched to yalebulldogblue.com via a WebFetch summary of its style — not copied text), Products (grid of cards from the API), Product Detail (image one side, description/price/sizes+stock table the other), Login and Create Account (UI-only stub forms, not wired to a backend yet). `ChatWidget` component bottom-right with open/close + local-only canned replies (no backend wiring yet, per the prompt).
- Verified end-to-end in a browser with both servers running: nav, home, products grid with real catalogue images/prices, product detail page, and the chat widget all work with no console errors.
- Added `README.md` with run instructions and `.claude/launch.json` for previewing the frontend.

## Problem 4

*(prompts go here)*

## Problem 4: Create account and login

**Prompt 1:**
> problem 4 is "Create account and login." we need to make a create-account and login flow:
>
> * create account: first name, last name, email, password (confirm password would be good too)
> * log in: email and password
>
> new accounts should go into the users table. make sure we store passwords securely - human and AI hackers shouldn't be able to get them.
>
> if you need a test user, the seed database has one we can use - email is test@campuscustoms.yale.edu and password is password
>
> check that login works as a user, and check that a new account you make also works.
>
> add to output/harness.md what we store for a user and how passwords are protected

*What was built:*
- Reverse-engineered the seeded test user's password hash (`test@campuscustoms.yale.edu` / `password`) to figure out the exact scheme already in use: PBKDF2-HMAC-SHA256, 120,000 iterations, format `pbkdf2_sha256$<salt>$<hex_digest>`. Matched that scheme in [backend/security.py](backend/security.py) so both the seeded account and new accounts work through the same login path.
- Added `POST /api/auth/register` and `POST /api/auth/login` to [backend/main.py](backend/main.py), using Pydantic models for validation (including a min-8-character password check and a password/confirm-password match check). Responses never include `password_hash`.
- Added frontend auth: [AuthContext.tsx](frontend/src/AuthContext.tsx) (tracks logged-in user, persisted in localStorage, no password/hash stored client-side), wired real submit handlers into [LoginPage.tsx](frontend/src/pages/LoginPage.tsx) and [CreateAccountPage.tsx](frontend/src/pages/CreateAccountPage.tsx), and updated [NavBar.tsx](frontend/src/components/NavBar.tsx) to show "Hi, {name}" + Log Out when signed in instead of the Login/Create Account links.
- Verified in the browser: logged in as the seed test user (worked, nav updated to "Hi, Test"), logged out, created a brand-new account through the UI (auto-logged in), logged out again, and logged back in with that same new account's credentials (worked independently of the auto-login) — confirming the full round trip. Also verified via curl that duplicate-email registration returns 409 and mismatched confirm-password returns 400. Test accounts created during verification were deleted from the db afterward so they don't pollute the seed data.
- Documented what's stored for a user and exactly how passwords are protected in [output/harness.md](output/harness.md#what-we-store-for-a-user-problem-4-create-account--login).

## Problem 5: PydanticAI agent backend

**Prompt 1:**
> problem 5: "PydanticAI agent backend". i want a pydanticai agent plugged into my front-end chat widget (so behind fast API). put the API app in backend/main.py - this will be the file we run with uvicorn. keep the agent as these four files next to it:
>
> * backend/prompts/prompt.md (system prompt - we'll work on this more later)
> * backend/agent.py (agent entry and wiring)
> * backend/tools.py (tools the agent can call)
> * backend/models.py (pydantic ai structured types)
>
> main.py should expose a chat route so a message from the website returns a reply from the agent. use whatever else you need for products/auth. use my AI model API key for the agent as we discussed earlier.
>
> put campus customs voice and safety basics into prompts/prompt.md - we'll expand this later.
>
> start/update types in models.py for chat replies and product cards as needed. in output/harness.md, document how the front end talks to fast api and how the agent is loaded, including the prompt file and model.
>
> the backend should run from the backend/ folder like this: uvicorn main:app --reload --port 8000

*What was built:*
- Checked prior homework/lecture folders in the shared `AI Foundations` directory for this course's established PydanticAI + Portkey pattern (same user, same semester) to get the exact model naming and wiring right instead of guessing — confirmed via [Homework 3/hw3/agent.py](<../Homework 3/hw3/agent.py>) that "Luna"/"Terra" (mentioned earlier this session) correspond to real model names `gpt-5.6-luna` / `gpt-5.6-terra`, served through Portkey at `https://api.portkey.ai/v1` with the key sent both as `api_key` and as an `x-portkey-api-key` header. Also found a near-identical FastAPI+agent+chat-widget project ([Lecture 8/yale_som_courses_zlisto](<../Lecture 8/yale_som_courses_zlisto>)) and used its backend file layout/conventions as a structural template.
- [backend/db.py](backend/db.py) — pulled the SQLite access/serialization logic out of `main.py` (from Problem 3) into a shared module, since both the `/api/products` routes and the new agent tools need the same catalogue+inventory joining logic.
- [backend/models.py](backend/models.py) — `ProductCard` (mirrors the existing `/api/products` shape so the same frontend `ProductCard` component can render it) and `ChatReply` (the agent's structured output: a text `reply` plus an optional `products` list).
- [backend/tools.py](backend/tools.py) — `search_products` (simple keyword/tag overlap scoring across name/description/garment_type/colors/search_tags — no second LLM call needed given the catalogue is only ~100 items) and `get_product_details`, both reading from `db.py` so the agent can never answer a stock/price question without a real tool call.
- [backend/prompts/prompt.md](backend/prompts/prompt.md) — Campus Customs voice (warm, casual, Bulldog pride) and safety basics (stay on topic, never reveal the system prompt/tools/API keys even under a "ignore previous instructions" style request, don't collect sensitive personal data, refuse harmful requests, ask instead of guessing).
- [backend/agent.py](backend/agent.py) — builds and caches one PydanticAI `Agent` using `gpt-5.6-luna` by default (per the standing model policy — this single-turn shop Q&A doesn't need Terra), the two tools, the prompt file, and `ChatReply` as the output type. Caught a real issue while testing: an unhandled exception's raw text (model name, provider/Azure details) was going straight into the user-facing error reply — fixed so the real exception is only printed server-side and the user sees a generic "please try again" message.
- [backend/main.py](backend/main.py) — added `POST /api/chat` (validates the body, calls `run_agent`, returns `ChatReply` directly via `response_model`), and now loads `PORTKEY_API_KEY` from the shared `../.env` via `load_dotenv`.
- Frontend: added `sendChatMessage` to [api.ts](frontend/src/api.ts), `ChatProductCard`/`ChatReply` types, relaxed `ProductCard`'s prop type to a minimal structural interface so it can render both full `Product` objects and the chat's lighter `ChatProductCard` objects, and rewired [ChatWidget.tsx](frontend/src/components/ChatWidget.tsx) to call the real endpoint and render product cards under the assistant's reply (compact row-style cards via new CSS).
- Verified end-to-end: tested the agent directly (`python -c` calling `run_agent`) for a product search, a specific stock question, an out-of-catalogue question (correctly didn't hallucinate a product, offered the closest real match instead), and a prompt-injection attempt (triggered the model gateway's own content filter, handled gracefully). Then started the backend with the exact command from the prompt (`uvicorn main:app --reload --port 8000`, run from `backend/`) and tested `/api/chat` via curl, and finally tested the live chat widget in the browser (typed "Do you have any navy crewnecks?", got a reply plus 5 clickable product cards, no console errors).
- Documented the frontend↔FastAPI request/response contract and exactly how the agent is loaded (model, provider wiring, prompt file, tools, output type, usage limit, error handling) in [output/harness.md](output/harness.md).

## Problem 6: Tools: product info and stock

**Prompt 1:**
> problem 6 is "Tools: product info and stock"
>
> we need to give the agent tools to look up real info from campus_customs.db:
>
> * product description
> * price
> * how many are in stock (by size when the customer asks)
>
> the agent must always use info from the database - never invent stock or price or anything else info. if a size is out of stock, it must say so clearly.
>
> add to prompts/prompt.md so the agent knows how to call for all of this stuff. add or update models.py too
>
> lastly, in output/harness.md, list each tool and explain which model fields we choose for lookup results and why
>
> tbh i am confused why we're doing this right now because i thought the agent could already do this? so also explain to me why we're doing this now

*Answered the "why now" question directly:* `get_product_details` (Problem 5) already pulled real description/price/inventory from the database, so the data itself was never fabricated — but it returned a raw `{size, quantity}` list and left the LLM to read it and decide how to phrase "in stock" vs. "sold out," which is a soft guarantee (it relies on the model reading numbers correctly every time, including under future prompt complexity or adversarial phrasing). This problem's real addition is `check_size_stock`, a tool that computes the in-stock/sold-out verdict and its exact wording in Python, not in the model — turning "never invent stock" into something structurally true instead of a prompt instruction the model is just supposed to follow.

*What was built:*
- [backend/models.py](backend/models.py) — added `StockCheck` (`product_id, size, found, quantity, in_stock, message`). `found` distinguishes "size doesn't exist for this product" from "exists but sold out"; `message` is the pre-phrased, ready-to-relay sentence.
- [backend/tools.py](backend/tools.py) — added `check_size_stock(product_id, size)`, handling all four cases deterministically: in stock, sold out (quantity 0), size not carried by this product (lists the real available sizes), and product id not found at all.
- [backend/agent.py](backend/agent.py) — registered the new tool, bumped the usage-limit comment/value from 6 to 8 to leave headroom for a 3-tool chain (search → details → stock check) plus the final structured answer.
- [backend/prompts/prompt.md](backend/prompts/prompt.md) — added explicit guidance: use `check_size_stock` for any size-specific question, relay its `message`/`in_stock` faithfully rather than recomputing from a raw quantity, and state sold-out/invalid-size results plainly rather than softening them.
- Verified: unit-tested `check_size_stock` directly for all four cases (in stock, sold out, invalid size, invalid product), then tested through the live agent (`run_agent`) for a sold-out-size question, an in-stock-size question, and an invalid-size question — all answered correctly and clearly. Confirmed the running `--reload` server picked up the changes via curl against `/api/chat`.
- Documented all three tools (`search_products`, `get_product_details`, `check_size_stock`) in [output/harness.md](output/harness.md) with a table of exactly which fields each returns and why those specific fields were chosen.

## Problem 7: Chat search that updates the page

**Prompt 1:**
> ok problem 7 now: "Chat search that updates the page"
>
> we want to make it so that when a customer asks about a type of item, the agent should search the catalogue and the website dynamically updates to show those matching items as product cards (including image, name, price, and short info). this is an API contract - the agent should return structured product matches and the front end will render them on the website.
>
> after the product cards are loaded, the same single-item page behavior from previously should still work. each product card, including the ones that the chatbot brings to the page, should still open the detailed view (large image and full info) when clicked.
>
> update prompts/prompt.md and output/harness.md so all of this and how search results reach the page are clear

*What was built:* the backend API contract (`ChatReply.products`) didn't need to change — it was already structured product data from Problem 5. This was a frontend wiring problem: getting that data out of the chat bubble and onto the actual page.
- [frontend/src/SearchResultsContext.tsx](frontend/src/SearchResultsContext.tsx) — new shared React context holding the latest chat search's `results`/`query`, wrapped around the app in [main.tsx](frontend/src/main.tsx).
- [ChatWidget.tsx](frontend/src/components/ChatWidget.tsx) — when a reply includes products, pushes them into the context and navigates to `/products`.
- [ProductsPage.tsx](frontend/src/pages/ProductsPage.tsx) — now checks the context first; if a chat search is active, shows those results (with a "Chat Search Results — showing N matches for '...'" banner and a "View all products" reset link) instead of the full fetched catalogue.
- [NavBar.tsx](frontend/src/components/NavBar.tsx) — clicking "Products" also calls `clearResults()`, so there's exactly one reset path (nav click or the banner link) shared through the same context method.
- [backend/prompts/prompt.md](backend/prompts/prompt.md) — added explicit guidance that for category-style questions, *every* relevant match must go in `products` (not just the ones named in the text reply), since the page only shows what's in that list.
- No changes needed for the single-item detail view: chat-driven cards use the same `ProductCard` component and `product_id`-based link as the normal catalogue grid, and `ProductDetailPage` always fetches fresh by id regardless of how the user got there — so "click a card, see full detail" kept working automatically.
- Verified live in the browser: asked the chat "Do you have any quarter-zips?" from the Home page → it navigated to Products and showed a "Chat Search Results" grid of 8 real cards; clicked one → correct detail page (price, description, colors, sizes/stock with a sold-out size shown correctly); clicked "View all products" → back to the full 102-item catalogue. No console errors.
- Documented the full producer→context→consumer flow and why the detail page needed no changes in [output/harness.md](output/harness.md).

## Problem 8: Customer memory

**Prompt 1:**
> ok question 8 is "Customer memory." when a shopper is logged in, their chat history should be saved in the database in an appropriate table and reloaded when they come back. the agent should know who is chatting (name, email). put that in agent deps or tools the agent can use. (side note: explain to me what agent deps are)
>
> there should be enough page context that if someone is on a product page and asks a question like "do you have this in pink?" the agent can tell which item they are referring to (you can put code into the agent context)
>
> guests should still be able to chat but we only need history for logged in users
>
> document in output/harness.md how user chat history is stored, what customer fields the agent sees, and how page context is passed

*Explained agent deps inline* (also captured in [output/harness.md](output/harness.md)): a typed object passed per-call via `run_sync(..., deps=...)` that tools/system-prompt functions read via `RunContext.deps` — never part of the conversation text, so the model can't mistake it for customer input or forget to look it up like it might forget to call a tool.

*What was built:*
- [backend/agent.py](backend/agent.py) — `ChatDeps` dataclass (`customer: CustomerContext | None`, `current_product_id: str | None`), plus two `@agent.system_prompt` functions that read it and inject who's chatting and what page they're on, computed with real DB-backed Python code at request time.
- [backend/models.py](backend/models.py) — `CustomerContext` (`id, name, email` only — never `password_hash` or anything else from `users`) and `ChatHistoryMessage` (for the history-reload endpoint).
- [backend/db.py](backend/db.py) — `fetch_user_by_id`, `fetch_chat_history` (oldest-first, optional limit), `save_chat_message`. No schema change needed — the seed `chat_messages` table from Problem 2 was already exactly the right shape for this.
- [backend/main.py](backend/main.py) — `POST /api/chat` now accepts `user_id`/`current_product_id`, only persists messages when `user_id` is present (guests stay ephemeral), and feeds the agent real conversational memory by replaying the last 12 stored messages as PydanticAI `message_history`. New `GET /api/chat/history?user_id=` for the frontend to reload the full visible log.
- Frontend: [ChatWidget.tsx](frontend/src/components/ChatWidget.tsx) derives the current product id from the URL (`useLocation` + a `/products/:id` regex match), sends it plus the logged-in user's id with every message, and reloads chat history via a `useEffect` keyed on the logged-in user.
- **Bug found and fixed during testing:** with only a system-prompt describing the current page, a logged-in customer whose replayed history had discussed a different product kept getting answered about *that* older product instead of the one on their current screen — the model weighted the conversational back-and-forth over the system instruction. Fixed by also prepending a page-context reminder directly onto that turn's message before sending it to the model (`_build_prompt` in `agent.py`) — the stored `chat_messages.content` stays the customer's original unmodified text; only what the model sees gets the reminder.
- Verified: guest chat persists nothing; logging in as the seed test user auto-reloaded their full saved conversation in the widget; asking "which of those hoodies did I just ask about?" correctly recalled the real prior conversation (and self-corrected a category mislabel); a guest on a product page got correctly product-specific answers with no page/name given explicitly; the history-vs-page-context conflict was reproduced, fixed, and reverified. Test accounts/messages created during verification were deleted from the db afterward.
- Documented all of it — deps, storage, customer fields, page-context mechanism including the bug — in [output/harness.md](output/harness.md).

## Problem 9: Usability improvements

**Prompt 1:**
> problem 9 is "Usability improvements"
>
> fire up the browser for me again so i can come up with some usability improvements

**Prompts 2-5 (follow-ups):** "no it's not working, fire it up again" → "no, not working" → (dismissed a diagnostic question) → a screenshot showing a blank "New Tab" with an empty address bar and only the server-status chip visible → "neither does anything" (after trying the suggested chip-click/URL-type workarounds) → "closed the pane entirely, restart it please" → still "no, not working" after restarting into the fresh pane.

*Why follow-ups were needed:* the dev server itself was confirmed healthy and rendering correctly every time from this session's side (verified repeatedly via screenshot), but the user's embedded browser pane kept opening as an unnavigated blank tab — a display glitch in the app's preview pane, not a server problem. Repeated restarts of the preview server didn't fix a client-side rendering issue. Eventually resolved by having the user bypass the embedded pane entirely and open `http://localhost:5173` directly in their own regular browser, which worked immediately.

**Prompt 6 (the actual task, after the browser was working):**
> ok yes that worked. alright back to our task -
>
> we need to make 2 front end and 2 back end/agent improvements in usability.
>
> front end:
> * i want little symbols/images on the main page under the headings like "built for every bulldog" - right now it looks too sparse
> * suggest another front end improvement and let's discuss before you implement it
>
> back end/agent: suggest 2 improvements that won't burn all my tokens but would improve the usability
>
> write in output/usability.md as you build what we added and why it helps a campus customs shopper or the business

*Discussion step:* presented options for frontend #2 (filter/sort on Products page, loading skeletons, or mobile hamburger nav) and for 2 backend/agent improvements (typo-tolerant search, quick-reply suggestions, in-memory catalogue cache, or low-stock urgency flag — all four scoped to add zero extra LLM calls). User picked: **filter/sort on Products page**, **typo-tolerant search**, and **low-stock urgency flag**.

*What was built:*
- **Frontend #1 — home page icons:** [FeatureIcon.tsx](frontend/src/components/FeatureIcon.tsx) (6 inline SVG icons: people, shield, hoodie, sparkle, ruler, chat) wired into [HomePage.tsx](frontend/src/pages/HomePage.tsx)'s six feature blocks, styled as white circular badges.
- **Frontend #2 — Products page filter/sort:** [ProductsPage.tsx](frontend/src/pages/ProductsPage.tsx) now has a toolbar with a garment-type filter and a price sort (Featured/Low-High/High-Low), derived from and applied to whichever product set is showing (full catalogue or an active chat search), resetting automatically when that set changes.
- **Backend/agent #1 — typo-tolerant search:** `search_products` ([backend/tools.py](backend/tools.py)) falls back to `difflib` fuzzy matching (cutoff 0.7) for query words with no exact hit, so "hoody"/"crewnek"/"sweatshit"-style typos still find the right products. Pure Python, zero added LLM calls.
- **Backend/agent #2 — low-stock urgency:** `check_size_stock` now returns `low_stock: bool` and phrases "only N left!" at ≤5 units; `ProductCard` gained a `low_stock_sizes` list. [prompts/prompt.md](backend/prompts/prompt.md) tells the agent it's fine to mention this for gentle urgency, sourced only from real tool data. Also pure Python, zero added LLM calls.
- **Bug hit during backend verification:** after restarting the backend, a stale duplicate process was still bound to port 8000 (recurring issue from Problem 8, now in memory) — caught it again, did a full clean kill-and-restart, and verified the *live* server (not just standalone script calls) had the latest code before trusting any test result.
- Verified end-to-end in the browser: icons render correctly on both home page sections; the Products toolbar correctly filters (102→18 for "pullover hoodie") and sorts (full catalogue re-ordered low-to-high by price) and also works scoped to a chat search's smaller result set (asking the bot "Show me fleece jackets" → toolbar/type-list scoped to just those 8 items); typo search and low-stock urgency both verified directly and through live agent replies. No console errors throughout.
- Documented all four improvements — what was built and why it helps a shopper or the business — in [output/usability.md](output/usability.md).

## Problem 10: Style the website

**Prompt 1:**
> problem 10: "style the website"
>
> let's make it look cooler - suggest a couple of imaginative and innovative (but low to moderate token usage) adjustments we can make to make this feel like a real storefront. we'll also write output/design.md to concisely explain what we changed and why it will help customers stick around and buy stuff

*Discussion step:* presented four options (collegiate display font, gold accent + micro-interactions, low-stock ribbon badges reusing Problem 9's data, or a trust-badge strip + textured hero). User picked the first three.

*What was built:*
- **Collegiate display font:** "Playfair Display" (Google Fonts) applied to all headings via a `--font-display` CSS variable; body text unchanged. [index.html](frontend/index.html), [index.css](frontend/src/index.css), [App.css](frontend/src/App.css).
- **Gold accent + micro-interactions:** new `--gold`/`--gold-dark` palette used on hovers (hero button, nav CTA, product cards, feature icons, links), plus product-card image zoom on hover and a subtle page fade-in on navigation.
- **Low-stock badge:** an amber "Selling Fast" corner badge on product cards.

*A real bug caught before shipping:* the badge was first wired to reuse Problem 9's `low_stock_sizes` (any single size ≤5 units) — checked the actual data and found this flagged **71 of 102 products (70%)**, which would make the badge meaningless/untrustworthy rather than a genuine urgency signal. Fixed by switching the trigger to **total stock across all sizes ≤25**, re-checked the real distribution, and confirmed this flags a credible **8 of 102 (~8%)**. The per-size data is still used as-is by the chat agent (Problem 9), where it's legitimately accurate for a specific-size question.

**Prompts 2+ (infrastructure detour):** while verifying the backend changes, hit a second, more severe version of the known `uvicorn --reload` unreliability (already in memory from Problem 8) — port 8000 got into a state where a confirmed brand-new, correct server process still served stale pre-edit data, while `Get-NetTCPConnection` showed the port "owned" by a PID that `Get-Process`/`tasklist` both confirmed didn't exist. Proved it was a port-level OS issue (not a code bug) by running the identical code on port 8001, where it worked immediately. Initially planned to just permanently switch the project to port 8001 and asked the user — **user corrected this: "wait no i need it to keep using 8000"** (presumably a fixed requirement), so reverted the plan. Tried the standard fix for this symptom (restarting the `winnat` service) — blocked by the sandbox (modifying a shared system service, correctly outside this session's permissions) and also turned out not to apply (the user's own attempt showed `winnat` wasn't even running). The only fix that worked was the user restarting their machine. Updated [the uvicorn-reload memory note](<../../../.claude/projects/C--Users-anany-Documents-AI-Foundations-Homework-4/memory/feedback_uvicorn_reload_unreliable.md>) with this escalation so a future session recognizes it faster as a port-level issue rather than re-debugging it as code.

*Final verification (after the restart):* confirmed port 8000 clean, started the backend there, and re-verified in the browser: all headings use the new serif, hover states show the gold accents, and exactly 8 of 102 products show the "Selling Fast" badge. No console errors.

Documented all three changes — what was built and why it helps customers/the business — in [output/design.md](output/design.md).

## Problem 11: Site testing (app check)

**Prompt 1:**
> problem 11 is called site testing (app check)
>
> we need screenshots and short captions for all of the following, to be documented in output/app_check.html (should be double clickable to open):
>
> * chat checking the inventory level of an item (from the DB)
> * dynamic search-result cards appearing after a category question (e.g., hoodies)
> * one of the usability features we just integrated
>
> the html needs to be easy to read and grade - a heading for each check, screenshot, 1-2 sentences on what the screenshot proves
>
> put screenshot image files in output/app_check_images/ and link them from app_check.html with relative paths

*What was built:*
- Captured three live screenshots in the browser against the running app (backend on :8000, frontend on :5173):
  1. Asked the chatbot a specific stock question ("Is the Basic Hoodie Big Yale in stock in a large?") — reply showed "8 available," matching the real `campus_customs.db` quantity.
  2. Asked a category question ("Do you have any hoodies?") from the Home page — captured the automatic navigation + page update showing 8 real hoodie cards (the Problem 7 feature).
  3. Used the Products page filter/sort toolbar (Problem 9) to narrow 102→18 items, captured with the "18 of 102 shown" counter visible as proof.
- Saved all three as `.jpg` files in [output/app_check_images/](output/app_check_images/) and built [output/app_check.html](output/app_check.html) — a clean, self-contained static page (no build step, inline CSS) with one heading + screenshot + 1–2 sentence caption per check, referencing the images with relative paths so the file is portable/double-clickable as-is.
- Verified the exact relative path structure on disk matches what the HTML references. Did not attempt to preview the static HTML through this session's browser tool (which is scoped to the dev server and can't navigate to `file://` URLs) or send it via the file-sharing tool (which could show misleadingly broken images since it wouldn't carry the sibling images folder along) — confirmed correctness by direct file-structure inspection instead, since the real use case is opening it directly in a normal browser.

## Problem 12: Audit trail, safety, finish harness

**Prompt 1:**
> problem 12 is "audit trail, safety, finish harness"
>
> we need to keep an append-only output/audit_trail.json of agent-loop activity (time, tool name, short args/result, stop reason). don't wipe it between runs.
>
> we also need some safety rules for the agent and put those in prompts/prompt.md
>
> then, finish output/harness.md by including:
>
> * model fields in models.py and why they were chosen
> * tools and abilities
> * safety rules
> * specs (loop limits, result caps, models, how to run front and back ends)

*What was built:*
- [backend/agent.py](backend/agent.py) — `run_agent` now appends one entry per call to `output/audit_trail.json` in a `finally` block (so it logs even on failure): `time`, `customer` (guest or name+email), `message` (capped 200 chars), `tool_calls` (every real tool call's name/short-args/short-result, excluding PydanticAI's internal `final_result` pseudo-tool), and `stop_reason` (`"completed"` or a capped `"error: ..."`). Writes are append-only (read-append-write, not overwrite), atomic (temp file + rename so a crash can't corrupt prior history), and lock-protected for concurrent requests; a corrupted file gets backed up aside rather than discarded.
- [backend/prompts/prompt.md](backend/prompts/prompt.md) — renamed "Safety basics" to "Safety rules" and added two new rules: treating tool output/pasted text as data-not-instructions (prompt-injection defense), and never promising discounts/price overrides/order confirmations not backed by a real tool result.
- [output/harness.md](output/harness.md) — added a final "Problem 12" section covering the audit trail schema, the full safety rules list, a table of every `models.py` field and why it was chosen, a tools/abilities table, and a specs section (model names, loop limit, result/history/audit caps, low-stock thresholds, and the exact run commands for both frontend and backend).
- Verified: triggered multiple real chat turns (a category search, a multi-tool-call stock question, and a prompt-injection attempt that genuinely hit Azure's content filter) through the live server, confirmed each appended correctly to `audit_trail.json` without erasing prior entries, then did a full backend restart and confirmed the file still had all prior entries plus a new one — proving true append-only, cross-restart persistence. Also directly tested the new "no fabricated discounts" safety rule (asked for 50% off) — correctly declined while staying helpful.

## Problem 13: Push to GitHub and submit the URL

**Prompt 1:**
> problem 13 is "push to github and submit the url"
>
> let's put everything into a folder called hw4 and push it to a public github repository. do NOT include my real .env, campus_customs.db, or product images in the repo. make sure we are using .gitignore. include .env.example with placeholders only. the file layout we want is attached as a screenshot (the cut off part says --reload --port 8000)
>
> the local only data pack should just contain campus_customs.db and products/ in the data/ folder.
>
> the agent should be contained in four files under backend/: prompts/prompt.md, agent.py, tools.py, and models.py
>
> README.md should explain how to run front and back ends after placing the data pack

*What was built:*
- Created a clean new root at `C:\Users\anany\Documents\AI Foundations\hw4` (sibling to the working `Homework 4` folder) and copied over exactly the files needed to match the requested layout: `AI_prompts.md`, `requirements.txt` (moved from `backend/` to the repo root), `.env.example`, `README.md`, `frontend/` (source + config only — no `node_modules`/`dist`), `backend/` (the four agent files plus the necessarily-supporting `main.py`, `db.py`, `security.py`), and `output/` (`harness.md`, `design.md`, `usability.md`, `app_check.html`, `app_check_images/`, `audit_trail.json`). Did **not** copy `venv/`, `data/` (db + product images), `node_modules/`, `.claude/`, or log files.
- Wrote a new root [.gitignore](.gitignore) excluding `.env`, the entire `data/` folder, `venv/`, `__pycache__/`, `frontend/node_modules`/`dist`, and `*.log`.
- Rewrote [README.md](README.md) for a fresh clone: where to place the data pack (`data/data/campus_customs.db` + `data/data/products/`), how to set up `.env` from `.env.example`, and exact run commands for both backend and frontend — removed the old README's reference to a shared `../.env` one level up, since that only made sense in the original course-folder layout, not a standalone public repo.
- Verified before committing: `find` for any `.env`/`__pycache__`/`node_modules`/`venv`/`data` turned up nothing, staged file list (`git status`) was exactly the 49 expected files, repo size ~507KB.
- Git/GitHub logistics: this machine had no `gh` CLI and no git identity configured. Per the git safety protocol, did not set git config myself — asked the user to run `git config --global user.name/user.email` themselves and to create the empty public repo on github.com, since both are account-level/identity actions outside what I should do unilaterally. User provided the remote: `https://github.com/ananya-yale/hw4.git`.
- Ran `git init`, `git add -A`, `git commit`, `git remote add origin ...`, `git push -u origin main` — pushed successfully on the first attempt (confirmed via `git ls-remote origin` matching the local commit hash exactly).
