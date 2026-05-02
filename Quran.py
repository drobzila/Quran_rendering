from __future__ import annotations

from manim import *
import glob
import json
import logging
import os
import subprocess
import sys
import textwrap
import random
import requests

from mutagen.mp3 import MP3
from pydub import AudioSegment
from pydub.effects import normalize

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ------------------- GLOBAL TITLE -------------------
VIDEO_TITLE = text   # 👈 مهم جداً للـ upload.py


# ------------------- Settings -------------------
font_name = "Amiri"
font_size_ayah = 72

wrap_width_chars = 42
max_lines_per_page = 5
line_spacing = 0.5

background_color = "#0b0f1a"
text_color = WHITE

reciter = "ar.husary"

normal_output = "Quran_Normal.mp4"
shorts_output = "Quran_Shorts.mp4"

MAX_DURATION = 20
USED_FILE = "used_ayahs.json"
TEMP_AUDIO = "temp.mp3"


# ------------------- Load Quran -------------------
with open("quran.json", "r", encoding="utf-8") as f:
    QURAN_DATA = json.load(f)


# ------------------- Used Ayahs -------------------
def load_used():
    if os.path.exists(USED_FILE):
        with open(USED_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_used(data):
    with open(USED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(data), f, ensure_ascii=False, indent=2)


# ------------------- Audio -------------------
def download_audio(surah: int, ayah: int, filename: str) -> str:
    url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/{reciter}"
    r = requests.get(url, timeout=20).json()
    audio_url = r["data"]["audio"]

    audio_data = requests.get(audio_url, timeout=20).content
    with open(filename, "wb") as f:
        f.write(audio_data)

    return filename


def get_duration(file):
    return MP3(file).info.length


def combine_audio(files: list[str], output="audio.mp3"):
    audio = AudioSegment.empty()

    for f in files:
        audio += AudioSegment.from_mp3(f)

    audio = normalize(audio)
    audio.export(output, format="mp3")

    return output


# ------------------- Random Ayah -------------------
def choose_random_ayah():
    global VIDEO_TITLE   # 👈 مهم

    used = load_used()
    candidates = []

    for s_idx, surah in enumerate(QURAN_DATA["data"]["surahs"], start=1):
        for a_idx, ayah in enumerate(surah["ayahs"], start=1):
            key = f"{s_idx}:{a_idx}"
            if key not in used:
                candidates.append((s_idx, a_idx, ayah["text"]))

    random.shuffle(candidates)

    for surah, ayah, text in candidates:
        try:
            download_audio(surah, ayah, TEMP_AUDIO)
            duration = get_duration(TEMP_AUDIO)

            if duration <= MAX_DURATION:
                used.add(f"{surah}:{ayah}")
                save_used(used)
                os.remove(TEMP_AUDIO)

                VIDEO_TITLE = text.strip()  # 👈 هنا العنوان = الآية

                return surah, ayah, text

            os.remove(TEMP_AUDIO)

        except Exception:
            continue

    raise Exception("❌ لم يتم العثور على آية مناسبة")


# ------------------- Text processing -------------------
def wrap_text(text: str) -> list[str]:
    text = " ".join(text.split())
    return textwrap.wrap(text, width=wrap_width_chars)


def paginate(lines: list[str]) -> list[list[str]]:
    return [
        lines[i:i + max_lines_per_page]
        for i in range(0, len(lines), max_lines_per_page)
    ]


def make_block(lines: list[str]) -> VGroup:
    texts = [
        Text(line, font=font_name, font_size=font_size_ayah, color=text_color)
        for line in lines
    ]

    block = VGroup(*texts).arrange(DOWN, buff=line_spacing)
    block.move_to(ORIGIN)

    return block


# ------------------- Scene -------------------
class QuranScene(Scene):
    def construct(self):
        self.camera.background_color = background_color

        surah, ayah, text = choose_random_ayah()

        audio_file = download_audio(surah, ayah, f"audio_{ayah}.mp3")
        audio_path = combine_audio([audio_file])
        audio_length = MP3(audio_path).info.length

        lines = wrap_text(text)
        pages = paginate(lines)

        per_page = max(audio_length / len(pages), 2.5)

        for page in pages:
            block = make_block(page)

            self.play(FadeIn(block), run_time=1)
            self.wait(per_page - 1)
            self.play(FadeOut(block), run_time=0.8)


# ------------------- Run -------------------
if __name__ == "__main__":
    subprocess.run(
        ["manim", "-qh", os.path.abspath(__file__), "QuranScene"],
        check=True
    )

    video = glob.glob("media/videos/**/*QuranScene.mp4", recursive=True)[0]

    subprocess.run([
        "ffmpeg", "-y",
        "-i", video,
        "-i", "audio.mp3",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        normal_output,
    ], check=True)

    subprocess.run([
        "ffmpeg", "-y",
        "-i", normal_output,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "-c:a", "copy",
        shorts_output,
    ], check=True)

    logger.info("✅ تم إنتاج فيديو قصير بنجاح")
