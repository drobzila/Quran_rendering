import pickle
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def load_creds():
    with open("token.pkl", "rb") as f:
        return pickle.load(f)


def get_title():
    if os.path.exists("title.txt"):
        with open("title.txt", "r", encoding="utf-8") as f:
            return f.read().strip()

    return "آية قرآنية قصيرة ❤️ #shorts"


def upload_video(file_path, title, description, privacy="public"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    creds = load_creds()
    youtube = build("youtube", "v3", credentials=creds)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
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
    print("📝 Title:", title)
    print("🔗 https://www.youtube.com/watch?v=" + response["id"])


if __name__ == "__main__":

    video_file = "Quran_Shorts.mp4"
    title = get_title()

    description = """
    
#quran #shorts #قرآن #islam
    """.strip()

    upload_video(video_file, title, description)
