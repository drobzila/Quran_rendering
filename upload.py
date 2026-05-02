import pickle
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ------------------- Load OAuth credentials -------------------
def load_creds():
    with open("token.pkl", "rb") as f:
        return pickle.load(f)


# ------------------- Get title from environment or fallback -------------------
def get_title():
    # الأفضل: من Quran.py عبر env أو import
    title = os.getenv("VIDEO_TITLE")

    if not title:
        # fallback إذا فشل
        title = "آية قرآنية قصيرة ❤️ #shorts"

    return title


# ------------------- Upload video -------------------
def upload_video(file_path, title, description, privacy="public"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Video not found: {file_path}")

    creds = load_creds()

    youtube = build("youtube", "v3", credentials=creds)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,   # 👈 الآية هنا
                "description": description,
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False
            }
        },
        media_body=MediaFileUpload(file_path)
    )

    response = request.execute()

    print("✅ Upload Successful!")
    print("🎬 Video ID:", response["id"])
    print("🔗 https://www.youtube.com/watch?v=" + response["id"])


# ------------------- MAIN -------------------
if __name__ == "__main__":

    video_file = "Quran_Shorts.mp4"

    title = get_title()

    description = """
تلاوة جميلة من القرآن الكريم 📖

#quran #shorts #قرآن #islam
    """.strip()

    upload_video(video_file, title, description)
