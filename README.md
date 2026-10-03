# Campus Customs

A Yale-branded apparel storefront with an AI shopping assistant: React + Vite + TypeScript frontend, FastAPI backend, and a PydanticAI agent that searches the catalogue and checks real inventory.

## 1. Place the data pack

This repo does **not** include the product database or images (they're excluded via `.gitignore`). Before running anything, place the data pack so it looks like this:

```
hw4/
└── data/
    └── data/
        ├── campus_customs.db
        └── products/
            ├── basic-hoodie-big-yale.jpg
            └── ... (one .jpg per product)
```

## 2. Set up your API key

Copy `.env.example` to `.env` in the project root and fill in your own key:

```bash
cp .env.example .env
```

```
PORTKEY_API_KEY=your-portkey-api-key-here
```

## 3. Run the backend

From the project root:

```bash
python -m venv venv
source venv/Scripts/activate   # Windows (Git Bash); use `venv\Scripts\activate` in cmd/PowerShell, or `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

The API is now at `http://localhost:8000` (docs at `/docs`).

## 4. Run the frontend

In a second terminal, from the project root:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The frontend talks to the backend at `http://localhost:8000` by default (override with a `VITE_API_URL` env var in `frontend/.env` if you run the backend elsewhere).

## Project layout

```
hw4/
├── AI_prompts.md          # Log of every prompt used to build this project
├── requirements.txt       # Backend Python dependencies
├── .env.example           # Copy to .env and fill in PORTKEY_API_KEY
├── frontend/               Vite + React + TypeScript app
├── backend/
│   ├── main.py             FastAPI app — run with: uvicorn main:app --reload --port 8000
│   ├── agent.py            PydanticAI agent wiring (model, tools, deps, audit trail)
│   ├── models.py           Structured types shared by the agent and API
│   ├── tools.py            Tools the agent can call (search, product lookup, stock check)
│   ├── prompts/prompt.md   Agent system prompt (voice + safety rules)
│   ├── db.py               Shared SQLite access
│   └── security.py         Password hashing
└── output/
    ├── harness.md           Full project documentation
    ├── design.md            Style/design pass notes
    ├── usability.md         Usability improvements notes
    ├── app_check.html       Screenshots + captions verifying the app works
    ├── app_check_images/
    └── audit_trail.json     Append-only log of every agent run
```

See [output/harness.md](output/harness.md) for full documentation of the data model, agent tools, safety rules, and specs.
