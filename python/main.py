from google import genai
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
app = fastapi.FastAPI()



load_dotenv()  
client = genai.Client(api_key= os.getenv("GEMINI_API_KEY"))
global supabase
supabase = create_client(os.getenv("SUPABASE_URL") , os.getenv("SUPABASE_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReelRequest(BaseModel):
    url: str



@app.post("/categorize")
async def categorize_video(request: ReelRequest):
    print(f"Downloading video from: {request.url}")
    
    # Download the video using the URL from the frontend
    unique_id = str(uuid.uuid4())
    download_instagram_video(request.url, output_dir=f"downloads/{unique_id}")

    downloads_folder = pathlib.Path(f"downloads/{unique_id}")
    video_files = list(downloads_folder.glob("*.mp4"))

    if not video_files:
        return {"summary": "Error: Could not download video.", "categories": [], "tags": []}
    
    latest_video = video_files[-1]
    print(f"Processing video: {latest_video.name}")

    video_bytes = open(latest_video, "rb").read()

 
    prompt = """
    Analyze this video. You MUST return ONLY a JSON object. Do not include markdown formatting like ```json.
    Use this exact structure:
    {
      "summary": "A 2-3 sentence summary of what happens in the video, its tone, and target audience.",
      "categories": ["Category 1", "Subcategory 2"],
      "tags": ["hashtag1", "hashtag2", "hashtag3"]
    }
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
        supabase.table("Reels").insert({
            "url" : request.url ,
            "summary" : result["summary"],
            "tags": result["tags"],
            "categories" : result["categories"]
        }).execute()

        return result
    except Exception as e:
        print(f"AI Error: {e}")
        return {
        "summary": "The AI is a bit sleepy right now (High Demand). Please try again in a moment!",
        "categories": ["Error"],
        "tags": ["TryAgain"]
    }
    

@app.get("/reels")
async def get_reels():
    result = supabase.table("Reels").select("*").execute()
    return result.data