# 🧠 Reel-Mind

**the AI-powered search engine for ur digital hoarding habits.**

ok real talk: ur "Saved" folder on instagram is literally a graveyard. u got a 3-year-old sourdough recipe, a workout u SWORE u'd do, and a "life hack" for a toaster u don't even own.

**Reel-Mind** uses AI to actually categorize these reels so u can find them again. think of it as a personal librarian for ur ADHD-fueled 2am scrolling sessions. except now it has a login page so ur saved reels are actually YOURS and not just vibes floating in a database.

---

![Main UI](screenshots/Basic-UI)
![Saved Reels](screenshots/Saved-reels.png)

## 🐣 the "Freshman" Disclaimer

still a freshman. still figuring things out. the codebase is maybe slightly less spaghetti than before but like... no promises.

- **The Code:** held together with duct tape, stackoverflow, and Claude (the AI not the person. well. both actually)
- **The Logic:** it works on my machine and that's good enough for now
- **The UI:** ok tbh this one actually looks kinda clean now ngl

---

## ✨ what's new (aka the "i actually did stuff" update)

### 🔐 Auth (yes really)

there's now a proper sign in / create account flow. ur reels are actually tied to ur account now instead of just... existing in the void. built with supabase auth.

![Login Screen](screenshots/login.png)

### 📚 Saved Reels Library

u can now view ALL ur categorized reels in one place. each card shows:
- the **summary** of what the reel is actually about (so u don't have to watch it again to remember)
- the **categories** gemini slapped on it (Technology, Software, etc)
- the **tags** for more specific vibes (#Dangerzone #sandbox #malware prevention etc)
- the **date** u saved it
- a button to go **view it on instagram**
- a **delete button** for when u realize u don't actually care about that reel anymore

### ⚙️ Settings page

there's a lil settings gear icon now. it exists. that's all i'll say for now

### 🚀 Actually Deployed Now

it's live. like, on the internet. for real people. wild.

---

## ⚙️ how it works (the "big brain" pipeline)

1. **The Handover:** u drop a url. app says "bet, i got it"
2. **The Heist (`yt-dlp`):** backend sneaks in and downloads the reel. digital repo man for ur memes
3. **The Interrogation (Gemini AI):** i basically tell gemini *"bro just tell me what this is and put it in a category, i am NOT rewatching 47 saved reels"*
4. **The Membership Check:** supabase auth makes sure ur actually logged in before saving anything
5. **The Archive (Supabase):** categories + tags + summary get saved to ur personal library in the db
6. **The Cleanup:** backend deletes the downloaded video immediately after. no hoarding on the server
7. **The Delivery:** fastapi sprints back to the frontend and ur reel shows up all neat and categorized

---

## 🛠️ the stack

- **Python & FastAPI** — the engine room. still fast, still forgiving when i forget a colon
- **yt-dlp** — heavy lifter that grabs the videos. legend
- **Gemini AI** — the actual brain. im just the guy who asked nicely
- **Supabase** — handles the db AND auth now. doing double duty. RLS enabled so ur data is actually urs
- **HTML/CSS/JS** — frontend looking cleaner than ever (claude assisted 🙏)
- **Railway** — where the backend lives now. real deployment hours
- **GitHub Pages** — serving the frontend. fast, free, zero config
- **Hopes and Dreams** — down to like 40% of the codebase now. progress.

---

## 🚀 how to use it

it's deployed. just go here:

**👉 [msjabata25.github.io/reelmind](https://msjabata25.github.io/reelmind)**

create an account, enter ur Gemini API key (free at [aistudio.google.com](https://aistudio.google.com)), paste a reel url, and boom.

---

## 🏗️ running locally (if u really want to)

```bash
# 1. clone the chaos
git clone https://github.com/msjabata25/Reel-Mind.git

# 2. get the python stuff
pip install -r requirements.txt
# go make a snack, it takes a sec

# 3. set up ur .env (IMPORTANT or nothing will work)
# SUPABASE_URL=your_url
# SUPABASE_KEY=your_service_role_key

# 4. fire it up
cd python
uvicorn main:app --reload

# 5. go to localhost:8000 and pray
```

note: `GEMINI_API_KEY` doesn't go in .env anymore — users bring their own key through the app.

---

## ⚠️ known issues / "features"

- **yt-dlp fragility:** instagram actively fights scrapers. if downloads start failing, update yt-dlp and try again
- **gemini json parsing:** gemini occasionally wraps its response in markdown fences despite being explicitly told not to. working on stripping those before parsing
- **session expiry:** supabase tokens expire after an hour. if u get a weird auth error after leaving the tab open, just sign in again
- **mobile layout:** it's... fine? mostly? squint a little

---

## 🏗️ roadmap (the "i have plans" section)

- [x] auth (sign in / create account)
- [x] saved reels library with categories + tags
- [x] delete saved reels
- [x] summary display on reel cards
- [x] search / filter ur saved reels by tag or category
- [x] RLS policies — ur data is actually urs
- [x] deployed (Railway backend + GitHub Pages frontend)
- [x] automatic video cleanup after processing
- [ ] TikTok + YouTube Shorts support (url validation already done, just needs testing)
- [ ] proper logging instead of `print("wtf happened")`
- [ ] react native app — mobile version
- [ ] maybe a chrome extension?? idk that sounds hard
- [ ] survive uni while also not getting left behind by the job market
- [ ] internship (still doubtful but the dream lives on)

---

## 🤝 contributing

**if ur a senior dev:** please look away. i am begging u

**if ur a fellow student:** we suffer together. PRs welcome, judgment not

---

*built with ❤️, ☕, way too many gemini api calls, and a very confused look on my face by [msjabata25](https://github.com/msjabata25)*

