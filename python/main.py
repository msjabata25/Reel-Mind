from google import genai
from fastapi import Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

app = fastapi.FastAPI()

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

CORS_ALLOWED_ORIGIN = [""]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    # Verify the user's session token
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
  "categories": ["Category 1", "Subcategory 2"],
  "tags": ["hashtag1", "hashtag2", "hashtag3"]
}

For the summary: write 2-3 sentences that feel like a sharp, specific observation from someone who actually watched the video.
Mention the exact subject, tool, dish, technique, or moment that makes this reel worth remembering.
Capture the creator's tone naturally — without exaggerating it or using casual filler phrases like 'pretty neat', 'this guy', 'absolutely', or 'super'.
Do not open with 'This video features...' or 'A person shows...'.
"""

    # Step 1: Gemini analysis
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

    # Step 2: Save to Supabase with user_id
    try:
        supabase.table("Reels").insert({
            "url":        request.url,
            "summary":    result["summary"],
            "tags":       result["tags"],
            "categories": result["categories"],
            "user_id":    user_id
        }).execute()
    except Exception as e:
        print(f"Supabase Error: {e}")
        result["_save_error"] = "Your reel was analyzed but couldn't be saved. Check your DB connection."

    return result


@app.get("/reels")
async def get_reels(authorization: str = Header(...)):
    try:
        user_id = get_user_id(authorization)
    except Exception:
        raise fastapi.HTTPException(status_code=401, detail="Invalid or expired session. Please sign in again.")

    # Only return this user's reels
    result = supabase.table("Reels").select("*").eq("user_id", user_id).execute()
    return result.data


@app.delete("/reels/{reel_id}")
async def delete_reel(reel_id: int, authorization: str = Header(...)):
    try:
        user_id = get_user_id(authorization)
    except Exception:
        raise fastapi.HTTPException(status_code=401, detail="Invalid or expired session. Please sign in again.")

    try:
        # Only delete if the reel belongs to this user
        supabase.table("Reels").delete().eq("id", reel_id).eq("user_id", user_id).execute()
        return {"success": True, "deleted_id": reel_id}
    except Exception as e:
        print(f"Delete Error: {e}")
        raise fastapi.HTTPException(status_code=500, detail="Failed to delete reel.")


# Serve frontend files from the web/ folder
app.mount("/", StaticFiles(directory="../web",), name="static")