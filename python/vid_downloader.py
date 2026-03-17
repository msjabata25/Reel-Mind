import sys
from pathlib import Path
import tempfile

import yt_dlp


def download_instagram_video(url: str, output_dir: str = "downloads") -> None:
	Path(output_dir).mkdir(parents=True, exist_ok=True)

	# Use cookies from Instagram auth (written by main.py)
	# Works cross-platform on Windows/Linux/Mac
	cookies_file = str(Path(tempfile.gettempdir()) / "instacookies.txt")

	options = {
		"outtmpl": f"{output_dir}/%(title).80s.%(ext)s",
		"format": "mp4/best",
		"noplaylist": True,
		"cookiefile": cookies_file,
	}

	with yt_dlp.YoutubeDL(options) as ydl:
		ydl.download([url])


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: python vid_dowloader.py <instagram_video_url>")
		sys.exit(1)

	try:
		download_instagram_video(sys.argv[1])
		print("Download complete.")
	except Exception as error:
		print(f"Download failed: {error}")
		sys.exit(1)
