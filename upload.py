import pickle
import os
from datetime import datetime, timezone
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def load_creds():
    with open("token.pkl", "rb") as f: return pickle.load(f)

def get_title():
    if os.path.exists("title.txt"):
        with open("title.txt", "r", encoding="utf-8") as f: return f.read().strip()
    return "آية قرآنية قصيرة ❤️ #shorts"

def upload_video(file_path, title, description, publish_at=None):
    if not os.path.exists(file_path): raise FileNotFoundError(file_path)
    youtube = build("youtube", "v3", credentials=load_creds())
    status = {"privacyStatus": "private" if publish_at else "public", "selfDeclaredMadeForKids": False}
    if publish_at:
        dt = datetime.fromisoformat(publish_at.replace("Z", "+00:00"))
        if dt <= datetime.now(timezone.utc): raise ValueError("PUBLISH_AT must be in the future")
        status["publishAt"] = dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    response = youtube.videos().insert(part="snippet,status", body={"snippet":{"title":title,"description":description,"categoryId":"22"},"status":status}, media_body=MediaFileUpload(file_path, resumable=True)).execute()
    url = "https://www.youtube.com/watch?v=" + response["id"]
    print("Scheduled:", status.get("publishAt", "public now"))
    print(url)
    with open("youtube_url.txt", "w", encoding="utf-8") as f: f.write(url)
    return response["id"], url

if __name__ == "__main__":
    upload_video(os.environ.get("VIDEO_FILE","Quran_Shorts.mp4"), get_title(), "#quran #shorts #قرآن #islam", os.environ.get("PUBLISH_AT","").strip() or None)
