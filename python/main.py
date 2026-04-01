from google import genai
from fastapi import Header
from fastapi.middleware.cors import CORSMiddleware
from google.genai import types
import pathlib
from vid_downloader import download_instagram_video
from dotenv import load_dotenv
import os
import fastapi
import json
from pydantic import BaseModel
from supabase import create_client
import uuid
import shutil
import tempfile





app = fastapi.FastAPI()

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
def getCookies():
    result = supabase.table('configs').select("value").eq("key" , "instagram_cookies").single().execute()
    cookies_path = pathlib.Path(tempfile.gettempdir()) / "instacookies.txt"
    with open(cookies_path, "w") as f:
        f.write(result.data["value"])

getCookies()

# Set ALLOWED_ORIGIN in your .env to your frontend URL.
# Example: ALLOWED_ORIGIN=https://yourusername.github.io
# Defaults to "*" (all origins) if not set — fine for local dev, not recommended for production.
allowed_origin = os.getenv("ALLOWED_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReelRequest(BaseModel):
    url: str
    api_key: str


class ValidateKeyRequest(BaseModel):
    api_key: str





def get_user_id(authorization: str) -> str:
    """Extract and verify the user from the Bearer token. Returns user_id."""
    token = authorization.replace("Bearer ", "").strip()
    user  = supabase.auth.get_user(token)
    return user.user.id


@app.post("/validate-key")
async def validate_key(request: ValidateKeyRequest):
    try:
        client = genai.Client(api_key=request.api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Reply with the single word: valid"
        )
        return {"valid": True}
    except Exception as e:
        error_msg = str(e).lower()
        print(f"Key validation error: {e}")
        if any(word in error_msg for word in ["api key", "unauthorized", "permission", "401", "403"]):
            raise fastapi.HTTPException(status_code=400, detail="Invalid API key. Please check and try again.")
        return {"valid": True}







@app.post("/categorize")
async def categorize_video(request: ReelRequest, authorization: str = Header(...)):
    try:
        user_id = get_user_id(authorization)
    except Exception:
        raise fastapi.HTTPException(status_code=401, detail="Invalid or expired session. Please sign in again.")

    print(f"Request from user: {user_id}")
    print(f"Downloading video from: {request.url}")

    client = genai.Client(api_key=request.api_key)

    unique_id = str(uuid.uuid4())
    download_instagram_video(request.url, output_dir=f"downloads/{unique_id}")

    downloads_folder = pathlib.Path(f"downloads/{unique_id}")
    video_files      = list(downloads_folder.glob("*.mp4"))

    if not video_files:
        return {"summary": "Error: Could not download video.", "categories": [], "tags": []}

    latest_video = video_files[-1]
    print(f"Processing video: {latest_video.name}")
    video_bytes = open(latest_video, "rb").read()

    prompt = """
Analyze this video. You MUST return ONLY a JSON object. Do not include markdown formatting like ```json.

Use this exact structure:
{
  "summary": "...",
  "tags": ["hashtag1", "hashtag2", "hashtag3"]
}

For the summary: write 2-3 sentences that feel like a sharp, specific observation from someone who actually watched the video.
Mention the exact subject, tool, dish, technique, or moment that makes this reel worth remembering.
Capture the creator's tone naturally — without exaggerating it or using casual filler phrases like 'pretty neat', 'this guy', 'absolutely', or 'super'.
Do not open with 'This video features...' or 'A person shows...'.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=types.Content(
                parts=[
                    types.Part(inline_data=types.Blob(data=video_bytes, mime_type="video/mp4")),
                    types.Part(text=prompt)
                ]
            )
        )
        result = json.loads(response.text)
        print(f"AI Response: {result}")
    except json.JSONDecodeError as e:
        print(f"Gemini returned invalid JSON: {e}")
        return {"summary": "AI returned an unexpected response. Please try again.", "categories": ["Error"], "tags": ["TryAgain"]}
    except Exception as e:
        print(f"Gemini Error: {e}")
        return {"summary": "The AI is a bit sleepy right now (High Demand). Please try again in a moment!", "categories": ["Error"], "tags": ["TryAgain"]}

    try:
        insert_result = supabase.table("Reels").insert({
            "url":        request.url,
            "summary":    result["summary"],
            "tags":       result.get("tags", []),
            "categories": [],
            "user_id":    user_id
        }).execute()
        result["id"] = insert_result.data[0]["id"]
    except Exception as e:
        print(f"Supabase Error: {e}")
        result["_save_error"] = "Your reel was analyzed but couldn't be saved. Check your DB connection."
    finally:
        try:
            shutil.rmtree(f"downloads/{unique_id}")
            print(f"Cleaned up downloads/{unique_id}")
        except Exception as e:
            print(f"Cleanup Error: {e}")

    return result


class CategorizeAIRequest(BaseModel):
    reel_id: int
    api_key: str


@app.post("/categorize-ai")
async def categorize_ai(request: CategorizeAIRequest, authorization: str = Header(...)):
    try:
        user_id = get_user_id(authorization)
    except Exception:
        raise fastapi.HTTPException(status_code=401, detail="Invalid or expired session. Please sign in again.")

    # Fetch the reel
    reel_result = supabase.table("Reels").select("*").eq("id", request.reel_id).eq("user_id", user_id).execute()
    if not reel_result.data:
        raise fastapi.HTTPException(status_code=404, detail="Reel not found.")
    reel = reel_result.data[0]

    # Fetch user's categories
    try:
        cats_result = supabase.table("categories").select("name").eq("user_id", user_id).execute()
        user_categories = [row["name"] for row in cats_result.data]
    except Exception:
        user_categories = []

    categories_instruction = (
        f"The user has these categories: {', '.join(user_categories)}. "
        "Pick the most fitting one. If none fit well, create a short new category name."
        if user_categories else
        "Create an appropriate short category name for this content."
    )

    prompt = f"""Based on this video summary, pick or create a single category.
{categories_instruction}

Summary: {reel['summary']}
Tags: {', '.join(reel.get('tags', []))}

You MUST return ONLY a JSON object. No markdown.
{{"category": "Category Name"}}"""

    try:
        client = genai.Client(api_key=request.api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        result = json.loads(response.text)
        category = result.get("category", "").strip()
        if not category:
            raise ValueError("Empty category")
    except Exception as e:
        print(f"Gemini categorize-ai error: {e}")
        raise fastapi.HTTPException(status_code=500, detail="AI could not determine a category. Please try again.")

    # Get current categories and append
    current_cats = reel.get("categories") or []
    if category not in current_cats:
        current_cats.append(category)

    # Save to reel
    supabase.table("Reels").update({"categories": current_cats}).eq("id", request.reel_id).eq("user_id", user_id).execute()

    # Auto-save category if new
    existing = supabase.table("categories").select("id").eq("user_id", user_id).eq("name", category).execute()
    if not existing.data:
        supabase.table("categories").insert({"user_id": user_id, "name": category}).execute()

    return {"category": category, "categories": current_cats}


@app.get("/categories")
async def get_categories(authorization: str = Header(...)):
    try:
        user_id = get_user_id(authorization)
    except Exception:
        raise fastapi.HTTPException(status_code=401, detail="Invalid or expired session. Please sign in again.")

    result = supabase.table("categories").select("*").eq("user_id", user_id).execute()
    return result.data


@app.post("/categories")
async def add_category(body: dict, authorization: str = Header(...)):
    try:
        user_id = get_user_id(authorization)
    except Exception:
        raise fastapi.HTTPException(status_code=401, detail="Invalid or expired session. Please sign in again.")

    name = body.get("name", "").strip()
    if not name:
        raise fastapi.HTTPException(status_code=400, detail="Category name cannot be empty.")

    # Check if already exists for this user
    existing = supabase.table("categories").select("id").eq("user_id", user_id).eq("name", name).execute()
    if existing.data:
        return existing.data[0]

    result = supabase.table("categories").insert({"user_id": user_id, "name": name}).execute()
    return result.data[0]


@app.get("/reels")
async def get_reels(authorization: str = Header(...)):
    try:
        user_id = get_user_id(authorization)
    except Exception:
        raise fastapi.HTTPException(status_code=401, detail="Invalid or expired session. Please sign in again.")

    result = supabase.table("Reels").select("*").eq("user_id", user_id).execute()
    return result.data


@app.patch("/reels/{reel_id}")
async def update_reel(reel_id: int, body: dict, authorization: str = Header(...)):
    try:
        user_id = get_user_id(authorization)
    except Exception:
        raise fastapi.HTTPException(status_code=401, detail="Invalid or expired session. Please sign in again.")

    categories = body.get("categories")
    if categories is None or not isinstance(categories, list):
        raise fastapi.HTTPException(status_code=400, detail="categories must be a list.")

    try:
        supabase.table("Reels").update({"categories": categories}).eq("id", reel_id).eq("user_id", user_id).execute()

        # Auto-save any new categories
        for cat in categories:
            existing = supabase.table("categories").select("id").eq("user_id", user_id).eq("name", cat).execute()
            if not existing.data:
                supabase.table("categories").insert({"user_id": user_id, "name": cat}).execute()

        return {"success": True}
    except Exception as e:
        print(f"Update Error: {e}")
        raise fastapi.HTTPException(status_code=500, detail="Failed to update reel.")


@app.delete("/reels/{reel_id}")
async def delete_reel(reel_id: int, authorization: str = Header(...)):
    try:
        user_id = get_user_id(authorization)
    except Exception:
        raise fastapi.HTTPException(status_code=401, detail="Invalid or expired session. Please sign in again.")

    try:
        supabase.table("Reels").delete().eq("id", reel_id).eq("user_id", user_id).execute()
        return {"success": True, "deleted_id": reel_id}
    except Exception as e:
        print(f"Delete Error: {e}")
        raise fastapi.HTTPException(status_code=500, detail="Failed to delete reel.")