# ReelMind — Project Progress

## What is ReelMind?
An AI-powered web app that takes an Instagram Reel URL, downloads it, analyzes it with Gemini, categorizes it, and saves it to a database — so users never lose a saved reel again.

**Core problem being solved:** People save hundreds of reels on Instagram but never come back to them, and accessing saved reels on Instagram is a hassle.

**Competitive landscape:** Similar apps exist (Memoray, Fofo, ReelRecall, Ordo) but the market is not saturated. Differentiators planned for ReelMind include multi-language support and a browser extension that surfaces saved reels while browsing the web.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| AI Analysis | Google Gemini 2.5 Flash (`gemini-2.5-flash`) |
| Video Downloading | yt-dlp |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth |
| Frontend | Vanilla HTML, CSS, JavaScript (ES Modules) |
| Frontend Hosting | GitHub Pages (`msjabata25.github.io/reelmind`) |
| Backend Hosting | Railway (`reel-mind-production.up.railway.app`) |
| Mobile (future) | React Native + Expo |
| Browser Extension (future) | Vanilla JS/TS |

---

## Project Structure

### Backend repo (Reel-Mind)
```
Reel-Mind/
├── python/
│   ├── main.py               # FastAPI backend
│   ├── vid_downloader.py     # yt-dlp download logic
│   ├── .env                  # API keys (never commit this)
│   └── downloads/            # Temp folder for downloaded videos (gitignored)
├── Procfile                  # Railway deployment config
├── requirements.txt
├── .gitignore
├── progress.md
└── README.md
```

### Frontend repo (reelmind)
```
reelmind/
├── auth.html                 # Login / signup page
├── auth.js
├── setup.html                # First-time Gemini API key setup
├── setup.js
├── index.html                # Main categorizer page
├── app.js
├── saved.html                # Saved reels library page
├── saved.js
├── styles.css                # Main page styles
└── saved_styles.css          # Saved page styles
```

---

## What's Built

### Backend (main.py)
- `POST /validate-key` — pings Gemini with the user's API key to confirm it works before saving
- `POST /categorize` — verifies session token, accepts a Reel URL + user's Gemini API key, downloads the video, sends it to Gemini for summary + tags only (no category), saves result to Supabase with empty categories array, returns JSON including the new reel `id`
- `POST /categorize-ai` — accepts `reel_id` + `api_key`, fetches reel summary from Supabase, sends summary + user's category list to Gemini as text (no video re-download), picks or creates a category, saves it to the reel and auto-saves new category to categories table
- `PATCH /reels/{id}` — verifies session token, updates the categories array of a reel, auto-saves any new categories to the categories table
- `GET /reels` — verifies session token, fetches only the authenticated user's reels from Supabase
- `DELETE /reels/{id}` — verifies session token, deletes a reel only if it belongs to the requesting user
- `GET /categories` — verifies session token, fetches all categories belonging to the authenticated user
- `POST /categories` — verifies session token, adds a new category for the user (duplicate-safe)
- CORS locked to `https://msjabata25.github.io`
- Environment variables via python-dotenv (Railway injects these in production)
- Unique download folders per request using `uuid` to avoid race conditions
- Automatic cleanup of downloaded videos after processing using `shutil.rmtree` in a `finally` block
- Separated Gemini vs Supabase error handling — DB failure no longer blocks AI result from returning
- Session token verification on all protected endpoints via `supabase.auth.get_user(token)`
- StaticFiles removed — frontend is served independently via GitHub Pages

### vid_downloader.py
- Takes a URL and output directory
- Downloads video using yt-dlp
- CLI compatible and importable as a module

### Supabase Database
- Table `Reels` (capital R — important, Supabase is case sensitive)
  - RLS enabled — users can only SELECT, INSERT, DELETE, and UPDATE their own reels
  - RLS expression: `auth.uid()::text = user_id`
  - Columns: `id` (auto), `created_at` (auto), `user_id`, `url`, `summary`, `tags` (text[]), `categories` (text[])
- Table `categories` (lowercase)
  - RLS enabled — users can only SELECT and INSERT their own categories
  - Columns: `id` (auto), `user_id` (uuid, default `auth.uid()`), `name` (text)
  - Auto-populated when user manually adds a category, picks one from the UI, or Gemini creates a new one
- Supabase **service role key** used in backend (required for RLS to work correctly on insert)

### Authentication
- `auth.html` + `auth.js` — login/signup page
  - Toggle between Sign In and Create Account modes
  - Email + password + confirm password on signup
  - Validates fields before submitting, shows password mismatch error
  - On success redirects to `setup.html` (or `index.html` if API key already saved)
  - Skips auth page entirely if session already exists
- Supabase Auth used for all session management
- JWT session token sent in `Authorization: Bearer` header with every backend request

### API Key Flow
- `setup.html` + `setup.js` — first-time Gemini API key entry
  - Only shown after successful login and only if no key is saved
  - Validates key against `/validate-key` before saving to localStorage
  - Show/hide toggle on key input
- Gear icon on `index.html` opens settings modal to update or remove key
- Sign out button clears session and API key, redirects to `auth.html`
- Gemini client initialized per-request using the user's own key — no API costs on the server

### Frontend
- `index.html` + `app.js` + `styles.css` — main categorizer UI
  - Auth guard — redirects to `auth.html` if no session, `setup.html` if no API key
  - URL input with validation (Instagram Reels, YouTube Shorts, TikTok), paste from clipboard, loading states, error handling
  - After analysis, displays summary + tags, then a **Categorize** section with user's category pills + "✨ Let AI decide" button
  - Picking a category pill calls `PATCH /reels/{id}` to save it; "Let AI decide" calls `/categorize-ai`
  - Summary is click-to-expand/collapse
  - Gear icon opens settings modal (update key, sign out)
  - Page scrolls correctly when result is long
- `saved.html` + `saved.js` + `saved_styles.css` — saved reels library
  - Auth guard on load
  - Fetches only the current user's reels
  - Horizontal scrollable **category filter pill row** — "All" + user's categories + "+" to add new ones inline
  - Filtering by category pill narrows the grid; combined with search for dual filtering
  - Search/filter bar — searches across summary, categories, and tags simultaneously
  - Live results count while filtering
  - Edit icon on each card's Categories section opens a **popover** with checkboxes for multi-category assignment + "✨ Let AI decide" option (calls `/categorize-ai`, pulses orange while thinking)
  - Delete button on each card with instant fade-out animation, restores card on failure
  - Dynamic redirect button — detects Instagram/TikTok/YouTube from URL and labels accordingly
  - Skeleton loading, empty state, no-results state, error state with retry

### AI Prompt & Categorization Flow
- `/categorize` prompt instructs Gemini to write summaries like a sharp, specific observation
  - Mentions the exact subject, dish, tool, or moment that makes the reel worth saving
  - Captures creator tone naturally — bans filler phrases like "pretty neat", "this guy", "absolutely"
  - Banned generic openers: "This video features...", "A person shows..."
  - Only returns `summary` + `tags` — categorization is a separate step
- `/categorize-ai` uses a lightweight text-only prompt (no video) — sends summary + tags + user's category list to Gemini, asks it to pick the best fit or create a new one
- Two-step categorization flow keeps initial scan fast and token-efficient

### Design
- Dark blue + orange color scheme
- Fonts: Syne (headings) + DM Sans (body)
- Glassmorphism cards, animated orbs, grain texture, gradient mesh background
- Consistent design language across all 4 pages

---

## Deployment

### Backend — Railway
- Deployed from the `Reel-Mind` GitHub repo
- `Procfile` at repo root: `web: cd python && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}`
- Environment variables set in Railway dashboard (not in .env)
- Auto-redeploys on every push to `main`
- Public URL: `https://reel-mind-production.up.railway.app`

### Frontend — GitHub Pages
- Deployed from the `reelmind` GitHub repo
- All HTML/CSS/JS files at repo root
- Served at: `https://msjabata25.github.io/reelmind`
- No build step needed — pure static files

---

## Known Issues / Technical Debt

1. **yt-dlp fragility** — Instagram occasionally breaks yt-dlp. Keep it updated in `requirements.txt` and handle failures gracefully.
2. **Gemini API key in localStorage** — fine for now, but consider encrypting or storing server-side tied to the user account in a future iteration.
3. **Gemini JSON parsing** — occasionally Gemini wraps response in ```json fences despite prompt instructions. Can be made more robust by stripping fences before parsing: `response.text.strip().removeprefix("```json").removesuffix("```").strip()`
4. **Session expiry** — Supabase tokens expire after 1 hour. Consider adding `onAuthStateChange` listener to auto-refresh tokens for long sessions.
5. **Railway free tier** — app may sleep after inactivity. First request after sleep will be slow. Upgrade to $5/month hobby plan if sharing with active users.

---

## Next Steps (in order)

1. **Smarter prompt + Router pattern** — pass 1 categorizes only (cheap), pass 2 uses a category-specific prompt to extract concrete info (URLs, recipes, tips, events)
2. **Static content support** — images, carousels, PDFs alongside video reels
3. **Share to app** — PWA + Web Share Target API so ReelMind appears in the mobile share sheet
4. **React Native app** — mobile version now that backend is stable
5. **Browser extension** — desktop companion that surfaces saved reels while browsing
6. **Multi-language support** — key differentiator from competitors
7. **Gemini JSON parsing hardening** — strip ```json fences before parsing to reduce edge case failures

---

## Environment Variables (Railway)

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key   ← service role, not anon key
```

Note: `GEMINI_API_KEY` is not needed — users supply their own key via the setup flow.

---

## How to Run Locally

```bash
# Install dependencies
pip install fastapi uvicorn python-dotenv google-generativeai supabase yt-dlp aiofiles

# Start the backend
cd python
uvicorn main:app --reload

# Open in browser
http://localhost:8000
```

For local frontend development, open HTML files via the localhost URL — not `file:///`. ES modules require an HTTP server.

---

## Notes
- Developer background: C++ primary, Python entry level (Cisco Python 1 Essentials badge)
- Frontend is handled by AI assistance — developer focuses on backend
- All JS files use ES Modules (`type="module"`) — required for Supabase SDK import
- Backend repo: https://github.com/msjabata25/Reel-Mind
- Frontend repo: https://github.com/msjabata25/reelmind