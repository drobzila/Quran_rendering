# -*- coding: utf-8 -*-
from manim import *
import logging
import requests
import glob
import json
import subprocess
import os
from mutagen.mp3 import MP3
from pydub import AudioSegment
import numpy as np
import sys
import random
import shutil

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ------------------- إعدادات -------------------
font_name = "Amiri"
font_size_ayah = 60
max_text_width = 8.2
max_lines_per_page = 4

shorts_output = "Quran_Shorts.mp4"

reciter = "ar.husary"
MAX_DURATION = 20
TEMP_AUDIO = "temp.mp3"
USED_FILE = "used_ayahs.json"


# ------------------- Manim Config (9:16 + Sync Stable) -------------------
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16
config.frame_rate = 60
config.background_color = BLACK


# ------------------- تنظيف الصوت القديم -------------------
for f in glob.glob("audio*.mp3"):
    os.remove(f)


# ------------------- تحميل القرآن -------------------
with open("quran.json", "r", encoding="utf-8") as f:
    QURAN_DATA = json.load(f)


def get_surah_name(surah):
    return QURAN_DATA["data"]["surahs"][surah - 1]["name"]


# ------------------- حفظ الآيات -------------------
def load_used():
    if os.path.exists(USED_FILE):
        with open(USED_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_used(data):
    with open(USED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(data), f, ensure_ascii=False, indent=2)


# ------------------- تحميل الصوت -------------------
def download_audio(surah, ayah, filename):
    url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/{reciter}"
    r = requests.get(url, timeout=20).json()
    audio_url = r["data"]["audio"]

    audio_data = requests.get(audio_url, timeout=20).content
    with open(filename, "wb") as f:
        f.write(audio_data)

    return filename


# ------------------- مدة الصوت -------------------
def get_audio_duration(file):
    return MP3(file).info.length


# ------------------- اختيار آية قصيرة -------------------
def choose_short_ayah():
    used = load_used()

    all_ayahs = []
    for s_idx, surah in enumerate(QURAN_DATA["data"]["surahs"], start=1):
        for a_idx, ayah in enumerate(surah["ayahs"], start=1):
            key = f"{s_idx}:{a_idx}"
            if key not in used:
                all_ayahs.append((s_idx, a_idx, ayah["text"]))

    random.shuffle(all_ayahs)

    for surah, ayah, text in all_ayahs[:200]:
        try:
            download_audio(surah, ayah, TEMP_AUDIO)
            duration = get_audio_duration(TEMP_AUDIO)

            if duration <= MAX_DURATION:
                used.add(f"{surah}:{ayah}")
                save_used(used)
                os.remove(TEMP_AUDIO)
                return surah, ayah, text

        except Exception:
            continue

    raise Exception("❌ لم يتم العثور على آية قصيرة")


# ------------------- أدوات -------------------
def to_arabic_indic_digits(value: str) -> str:
    return str(value).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))


def ayah_number_circle(number):
    circle = Circle(radius=0.35, color=GOLD, stroke_width=3)
    number_text = Text(number, font=font_name, font_size=28, color=GOLD)
    number_text.move_to(circle.get_center())
    return VGroup(circle, number_text)


def split_text_manim(text, font, font_size, max_width):
    words = text.split()
    lines, current = [], []

    def measure(t):
        return MarkupText(t, font=font, font_size=font_size).width

    for word in words:
        candidate = " ".join(current + [word])
        if current and measure(candidate) > max_width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)

    if current:
        lines.append(" ".join(current))

    return lines


def build_background(width=9, height=16):
    h, w = 1920, 1080
    noise = np.random.normal(0, 1, (h, w)).astype(np.float32)
    noise = (noise - noise.min()) / (noise.max() - noise.min() + 1e-8)
    rgb = (noise * 14).astype(np.uint8)

    rgba = np.stack([rgb, rgb, rgb, np.full_like(rgb, 18)], axis=-1)

    base = Rectangle(width=width, height=height, fill_color=BLACK, fill_opacity=1, stroke_width=0)
    overlay = ImageMobject(rgba).set_height(height).set_width(width).set_opacity(0.25)
    vignette = Rectangle(width=width, height=height, fill_color=BLACK, fill_opacity=0.15, stroke_width=0)

    return Group(base, overlay, vignette)


# ------------------- المشهد (FULL SYNC) -------------------
class QuranShortScene(Scene):
    def construct(self):
        self.camera.background_color = BLACK

        bg = build_background()
        self.add(bg)

        surah, ayah, text = choose_short_ayah()

        audio_path = download_audio(surah, ayah, f"audio_{ayah}.mp3")

        # 🎧 Add audio directly (NO ffmpeg)
        self.add_sound(os.path.abspath(audio_path))

        audio_length = MP3(audio_path).info.length
        ayah_label = to_arabic_indic_digits(str(ayah))

        wrapped_lines = split_text_manim(
            text, font_name, font_size_ayah, max_text_width
        )

        pages = [
            wrapped_lines[i:i + max_lines_per_page]
            for i in range(0, len(wrapped_lines), max_lines_per_page)
        ]

        per_page = audio_length / max(len(pages), 1)

        # 🎯 FULL SYNC LOOP
        for page in pages:

            text_block = (
                MarkupText(
                    " ".join(page),
                    font=font_name,
                    font_size=font_size_ayah,
                )
                .move_to(ORIGIN + UP * 0.5)
            )

            ayah_circle = ayah_number_circle(ayah_label).next_to(text_block, LEFT)

            self.play(FadeIn(text_block), FadeIn(ayah_circle))
            self.wait(per_page)
            self.play(FadeOut(text_block), FadeOut(ayah_circle))


# ------------------- التنفيذ -------------------
if __name__ == "__main__":
    subprocess.run(
        [
            "manim",
            os.path.abspath(__file__),
            "QuranShortScene",
            "-r",
            "1080,1920",
            "--format",
            "mp4",
        ],
        check=True,
    )

    # 📦 استخراج الفيديو النهائي
    videos = glob.glob("media/videos/**/*.mp4", recursive=True)
    video = sorted(videos)[-1]

    shutil.copy(video, "Quran_Shorts.mp4")

    logger.info("✅ Shorts جاهز مع صوت + فيديو متزامن 100%")
