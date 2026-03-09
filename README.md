# 🧠 Reel-Mind 

**The AI-powered search engine for your digital hoarding habits.**

Let’s be honest: your "Saved" folder on Instagram is a graveyard. You’ve got a 3-year-old recipe for sourdough, a workout routine you’ll never do, and a "life hack" for cleaning a toaster that you don't even own. 

**Reel-Mind** uses AI to actually categorize these reels so you can find them later. It’s like a personal librarian for your ADHD-fueled scrolling sessions.
---
![App Banner or Screenshot Placeholder](screenshots/Basic-UI)

## 🐣 The "Freshman" Disclaimer
I am a freshman. I just learned what a "POST request" is like... three days ago. 
* **The Code:** Probably looks like a bowl of spaghetti dropped from a height of six feet.
* **The Logic:** Mostly held together by Stack Overflow threads and sheer willpower.
* **The UI:** If it looks weird on your screen, try squinting. It helps.

---

## ⚙️ How It Works (The "Big Brain" Logic)

I’m not a wizard; I’m just really good at connecting things that are smarter than me. Here is the life cycle of a reel in this app:



1.  **The Handover:** You give the app a URL. The app says "Thanks, I'll take it from here."
2.  **The Heist (`yt-dlp`):** My backend uses `yt-dlp` to sneakily download the reel. It’s like a digital repo man, but for your memes.
3.  **The Interrogation (Gemini AI):** I send that video file over to **Gemini**. I basically ask the AI, *"Yo , just place this into a category cuz I'm lazy to do that myself so i dont absolutely not forget about in the next 5 mins"* 4.  **The Report:** Gemini just places it in it's own neat little digital shelf (I swear i have more plans for this im just limited by my short attention span and terrible coding skills). 
5.  **The Delivery:** **FastAPI** catches that info and sprints back to the **HTML/CSS/JS** frontend to show you your neatly categorized reel.

![App in use](screenshots/In-use-screenshot)
---

## 🛠️ The "Stack"
I kept it simple because my brain can only handle so many syntax errors at once:

* **Python & FastAPI:** The engine room. Fast, efficient, and surprisingly forgiving when I forget a comma.
* **yt-dlp:** The heavy lifter that actually grabs the videos.
* **Gemini AI:** The actual brain of the operation. I’m just the guy holding the flashlight.
* **HTML/CSS/JS:** Where I let my best friend Claudius write the front end , becuase this project will never leave  my computer if I was in charge of it.
* **Hopes and Dreams:** Roughly 65% of the codebase.
* **SupaBase:** Cuz why not.

---

## 🚀 How to Run (Maybe)
I’m still figuring out how deployment works, so we’re running this locally like it’s 2005.

1.  **Clone the chaos:**
    ```bash
    git clone [https://github.com/msjabata25/Reel-Mind.git](https://github.com/msjabata25/Reel-Mind.git)
    ```
2.  **Get the Python stuff:**
    ```bash
    pip install -r requirements.txt
    # If this takes forever, go grab a snack. 
    ```
3.  **Fire up the FastAPI engine:**
    ```bash
    cd python
    uvicorn main:app --reload
    ```
4.  **Open your browser:** Go to `localhost:8000` and pray you don't see a 404.

---

## ⚠️ Known Issues / "Features"
* **Security Issues:** It does have a lot of bad practices for production, but since this isn't my million dollar startup idea, I won't bother till it's actually done. The main one being RLS disabled on my supabse , but that will be changed with before proper policies before any real users.
*  **Broad except blocks:**  Yes, one error from gemini might just take down the entire app , which i may or may not have placed gemini and supabase under the same handler (dont roast me I'm new to this).
*  **No Auth yet:** Which is excepted cuz of how bare bones the project is now. 

---

## 🏗️ Future Plans (Roadmap to Greatness)
- [ ] Actually figure out how authentication works and proper security for my project.
- [ ] Stop using `print()` for debugging and learn what "logging" is. (I still don't know yet)
- [ ] Survive Uni on top of desperately trying to keep up with the ever developing job market.
- [ ] Maybe, and I mean MAYBE, I'll get an internship. (Highly doubt it at the time I'm writing this but a man can dream)

---

## 🤝 Contributing
If you’re a senior dev: **Please look away.** My code is painful to look at and is formated using ai (and I'm not ashamed of that)

If you’re a fellow student: **Let's suffer together.** Feel free to open a PR if you find a way to make my error handling less embarrassing.

---
*Created with ❤️, ☕, and a very confused look on my face by [msjabata25](https://github.com/msjabata25).*
