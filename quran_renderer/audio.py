from __future__ import annotations
import os
import requests
from mutagen.mp3 import MP3
from .config import RECITER

RECITER_NAMES = {
    "ar.husary": "الحصري",
    "ar.abdulbasitmurattal": "عبد الباسط عبد الصمد",
    "ar.minshawi": "المنشاوي",
    "ar.mahermuaiqly": "ماهر المعيقلي",
}

def download_audio(surah: int, ayah: int, filename: str) -> str:
    reciter = os.environ.get("QURAN_RECITER", RECITER)
    url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/{reciter}"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    audio_url = response.json().get("data", {}).get("audio")
    if not audio_url:
        raise RuntimeError(f"لا يوجد صوت للآية {surah}:{ayah} بالقارئ {reciter}")
    audio_response = requests.get(audio_url, timeout=30)
    audio_response.raise_for_status()
    with open(filename, "wb") as output:
        output.write(audio_response.content)
    return filename


def get_duration(filename: str) -> float:
    return float(MP3(filename).info.length)


def build_title(surah_name: str, ayah: int, reciter_id: str) -> str:
    """Generate a consistent title format for both daily videos."""
    surah = " ".join(surah_name.split())
    title = f"🌿 سورة {surah} | الآية {ayah} — تلاوة تشرح الصدر"
    suffix = " #قرآن #Shorts"
    return title[: 100 - len(suffix)].strip() + suffix
