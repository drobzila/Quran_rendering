from __future__ import annotations
import os\nimport requests
from mutagen.mp3 import MP3
from .config import RECITER
def download_audio(surah: int, ayah: int, filename: str) -> str:
    reciter = os.environ.get("QURAN_RECITER", RECITER)\n    url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/{reciter}"
    response = requests.get(url, timeout=20); response.raise_for_status()
    audio_url = response.json()["data"]["audio"]
    audio_response = requests.get(audio_url, timeout=30); audio_response.raise_for_status()
    with open(filename, "wb") as output: output.write(audio_response.content)
    return filename
def get_duration(filename: str) -> float:
    return float(MP3(filename).info.length)
