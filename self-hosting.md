# 🏗️ Self-Hosting Reel-Mind

**so u want to run ur own instance. respect.**

fair warning: this isn't a one-click deploy. u'll be touching supabase, railway, github pages, and a `.env` file. if that sounds scary, grab a snack first. if it doesn't, u probably already have 40 tabs open.

---

## 🧰 what u need before u start

- a [Supabase](https://supabase.com) account — free tier is fine
- a [Railway](https://railway.app) account — free tier is fine
- a [Google AI Studio](https://aistudio.google.com) account — for testing. ur users bring their own keys at runtime
- somewhere to host the frontend — [GitHub Pages](https://pages.github.com) is what this guide assumes. free, zero config, the goat.

---

## step 1 — supabase setup 🗄️

### 1.1 create a project

go to [supabase.com](https://supabase.com), hit **New Project**, pick a region near u. save ur database password somewhere. plz don't forget it dude. not fun to get it back trust me.

### 1.2 create the tables

go to the **SQL Editor** in ur supabase dashboard and run this:

```sql
-- the main reels table
create table "Reels" (
  id bigint generated always as identity primary key,
  created_at timestamptz default now(),
  url text not null,
  summary text,
  tags text[],
  categories text[],
  user_id uuid references auth.users(id) on delete cascade
);

-- user categories
create table categories (
  id bigint generated always as identity primary key,
  created_at timestamptz default now(),
  name text not null,
  user_id uuid references auth.users(id) on delete cascade
);

-- app config (instagram cookies live here)
create table configs (
  id bigint generated always as identity primary key,
  key text unique not null,
  value text not null
);
```

note: `"Reels"` is case-sensitive. capital R or it breaks. u've been warned. Ps. if you understand how to use supabase, you can do this step with the visual interface. 

### 1.3 enable RLS (so ur users' data is actually theirs)

```sql
-- lock down reels
alter table "Reels" enable row level security;
create policy "Users can manage their own reels"
  on "Reels" for all
  using (auth.uid() = user_id);

-- lock down categories
alter table categories enable row level security;
create policy "Users can manage their own categories"
  on categories for all
  using (auth.uid() = user_id);

-- configs: backend-only. no public access.
alter table configs enable row level security;
```

### 1.4 seed ur instagram cookies
this step is all cuz instagram decided to act like a damn bouncer to their data. 
reel-mind uses yt-dlp + ur instagram cookies to download reels. export them as a Netscape-format `.txt` file (any browser extension like **Get cookies.txt LOCALLY** works), then shove the contents into the db:

```sql
insert into configs (key, value)
values ('instagram_cookies', 'PASTE UR COOKIE FILE CONTENTS HERE');
```

> ⚠️ instagram sessions expire. if downloads start failing out of nowhere, this is probably why. re-export ur cookies and update this row.

### 1.5 grab ur API keys

go to **Settings → API** in ur supabase dashboard and copy:

| what | where it goes |
|---|---|
| **Project URL** | `SUPABASE_URL` in backend env |
| **anon / public key** | `SUPABASE_ANON_KEY` in `config.js` |
| **service_role key** | `SUPABASE_KEY` in backend env — never expose this publicly |

### 1.6 enable email auth

**Authentication → Providers → Email** — make sure it's on. if u want to skip email confirmation during testing, go to **Authentication → Settings** and turn it off.

---

## step 2 — deploy the backend 🚂

### 2.1 fork and clone

```bash
git clone https://github.com/your-fork/Reel-Mind.git
cd Reel-Mind
```

### 2.2 deploy to railway

1. go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. select ur fork
3. railway auto-detects the python app and deploys it. 

### 2.3 set ur environment variables

in ur railway project go to **Variables** and add these:

| variable | value |
|---|---|
| `SUPABASE_URL` | ur supabase project URL |
| `SUPABASE_KEY` | ur supabase **service_role** key |
| `ALLOWED_ORIGIN` | ur frontend URL e.g. `https://yourusername.github.io` |

> use `*` for `ALLOWED_ORIGIN` during local dev only. lock it down before u go live.

### 2.4 copy ur backend URL

railway gives u a public URL like `https://your-app.up.railway.app` once it's deployed. copy it. u need it in the next step.

---

## step 3 — set up the frontend 🖥️

### 3.1 fork and clone the frontend repo

```bash
git clone https://github.com/your-fork/reelmind-frontend.git
cd reelmind-frontend
```

### 3.2 create ur config file

```bash
cp config.example.js config.js
```

open `config.js` and fill in ur values:

```js
export const CONFIG = {
  API_BASE:          'https://your-app.up.railway.app',
  SUPABASE_URL:      'https://your-project-ref.supabase.co',
  SUPABASE_ANON_KEY: 'your-anon-key-here',
};
```

`config.js` is gitignored. it will never be committed. don't remove it from `.gitignore` or u'll be leaking ur keys to the internet and that's a bad time.
I didn't do it cuz i have nothing to show. it's just placeholder text. go focus on deploying yours and stop looking at mine.

### 3.3 deploy to github pages

push to main and let the github actions workflow handle the rest:

```bash
git add .
git commit -m "configure for self-hosting"
git push
```

ur site will be live at `https://yourusername.github.io/reelmind` (or whatever ur pages URL is configured to).

---

## step 4 — test it 🧪

1. open ur frontend URL
2. create an account
3. on the setup screen, enter a [Gemini API key](https://aistudio.google.com/app/apikey) — every user brings their own, that's the whole bit
4. paste an instagram reel URL and hit analyze
5. if it works: good. u somehow didnt mess it up (or did you 🤨)
6. if it doesn't: see below (Ps. youre okay, we all make mistakes. but i look cooler when i do them , not you)

---

## ⚠️ when things go wrong (and they will)

**downloads failing / yt-dlp errors**
ur instagram cookies expired. re-export from ur browser and update the `configs` table. happens more than u'd like.

**CORS error in the browser console**
`ALLOWED_ORIGIN` in railway doesn't match ur frontend URL exactly. check for trailing slashes, wrong protocol, typos. it's always something dumb.

**401 Unauthorized from the backend**
supabase session token isn't going through correctly. make sure ur logged in and that `SUPABASE_URL` + `SUPABASE_ANON_KEY` in `config.js` actually match ur project.

**`relation "Reels" does not exist`**
u created the table as `reels` (lowercase). it's case-sensitive. drop it and re-run the SQL from step 1.2 with the capital R.

**AI categorization not working**
the gemini key is user-supplied at runtime. make sure the user has entered a valid key in the settings modal. u can test keys at [aistudio.google.com](https://aistudio.google.com).

---

## 🧠 how it all fits together

```
Frontend (GitHub Pages)
    │
    │  Bearer token (Supabase JWT)
    ▼
Backend (Railway / FastAPI)
    ├── validates token with Supabase Auth
    ├── downloads video via yt-dlp + instagram cookies
    ├── sends video to Gemini (user's own API key)
    └── saves results to Supabase DB (scoped to user via RLS)
```

the backend never stores gemini keys. they're passed per-request and immediately used. ur users own their data, the db is locked down by RLS, and the downloaded video gets deleted right after processing.

---

## 🤝 contributing

if u self-host and add something cool, PRs are welcome. if u add a new env variable, update this guide and `config.example.js` too or ur PR is getting left on read. 

---

*if this guide saved u 3 hours of confusion, consider leaving a ⭐ on the repo. if it didn't, sorry. youre the problem.*
