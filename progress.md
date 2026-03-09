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
| AI Analysis | Google Gemini 2.0 Flash (`gemini-2.0-flash`) |
| Video Downloading | yt-dlp |
| Database | Supabase (PostgreSQL) |
| Frontend | Vanilla HTML, CSS, JavaScript |
| Auth (planned) | Supabase Auth |
| Mobile (future) | React Native + Expo |
| Browser Extension (future) | Vanilla JS/TS |

---

## Project Structure

```
project/
├── main.py               # FastAPI backend
├── vid_downloader.py     # yt-dlp download logic
├── index.html            # Main categorizer page
├── saved.html            # Saved reels library page
├── app.js                # Frontend JS for index.html
├── styles.css            # Shared styles
├── .env                  # API keys (never commit this)
├── .gitignore            # Ignores .env, downloads/, __pycache__/
└── downloads/            # Temp folder for downloaded videos (gitignored)
```

---

## What's Built So Far

### Backend (main.py)
- `POST /categorize` — accepts a Reel URL, downloads the video, sends it to Gemini, saves result to Supabase, returns JSON
- `GET /reels` — fetches all saved reels from Supabase and returns them
- CORS middleware enabled (allow_origins=["*"] — needs to be locked down before production)
- Environment variables via python-dotenv
- Unique download folders per request using `uuid` to avoid race conditions
- Error handling with try/except (note: currently one broad except block catches both Gemini and Supabase errors — should be separated later)

### vid_downloader.py
- Takes a URL and output directory
- Downloads video using yt-dlp
- CLI compatible and importable as a module

### Supabase Database
- Table name: `Reels` (capital R — important, Supabase is case sensitive)
- Row Level Security (RLS): currently **disabled** for development — must re-enable before production
- Columns: `id` (auto), `created_at` (auto), `user_id` (nullable, placeholder for auth), `url`, `summary`, `tags` (text[]), `categories` (text[])

### Frontend
- `index.html` + `app.js` + `styles.css` — main categorizer UI
  - URL input with validation, paste from clipboard, loading states, error handling
  - Displays AI result (summary, categories, tags) after analysis
  - Button to navigate to saved reels page
- `saved.html` — saved reels library page
  - Fetches from `GET /reels` on load
  - Renders a card per reel with summary, categories, tags, date, and "View on Instagram" link
  - Skeleton loading state, empty state, error state with retry

### Design
- Dark blue + orange color scheme
- Fonts: Syne (headings) + DM Sans (body)
- Glassmorphism cards, animated orbs, grain texture, gradient mesh background

---

## Known Issues / Technical Debt

1. **Broad except block** — Gemini errors and Supabase errors are caught by the same handler. Should be separated so a DB failure doesn't block the AI result from reaching the user.
2. **RLS disabled** — Supabase Row Level Security is off. Fine for dev, must be re-enabled with proper policies before any real users.
3. **CORS wildcard** — `allow_origins=["*"]` needs to be replaced with the actual frontend domain before production.
4. **No auth yet** — `user_id` column exists in the DB but is unused. All reels are shared globally right now.
5. **yt-dlp fragility** — Instagram occasionally breaks yt-dlp. Keep it updated and handle failures gracefully.
6. **model name** — make sure model is set to `gemini-2.0-flash`, not `gemini-3-flash-preview` (invalid).

---

## Next Steps (in order)

1. **User authentication** via Supabase Auth — so each user has their own library
2. **Populate user_id** on insert once auth is in place
3. **RLS policies** — re-enable RLS and write policies so users only see their own reels
4. **Separate error handling** in the `/categorize` endpoint
5. **TikTok + YouTube Shorts support** — yt-dlp already supports these, just update the URL validation in the frontend
6. **Deployment** — host the backend (Railway or Render) and serve the frontend statically
7. **React Native app** — mobile version once the backend is stable
8. **Browser extension** — desktop companion that surfaces saved reels while browsing

---

## Environment Variables needed in .env

```
GEMINI_API_KEY=your_gemini_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

---

## How to Run Locally

```bash
# Install dependencies
pip install fastapi uvicorn python-dotenv google-generativeai supabase yt-dlp

# Start the backend
uvicorn main:app --reload

# Open index.html directly in your browser (do NOT use Live Server — it causes page refresh conflicts)
```

---

## Notes
- Developer background: C++ primary, Python entry level (Cisco Python 1 Essentials badge)
- Frontend is handled by AI assistance — developer focuses on backend
- Repo: https://github.com/msjabata25/Reel-Mind