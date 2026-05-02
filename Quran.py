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
from pydub.effects import normalize
import numpy as np
import sys
import random

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
# Keep within frame_width to avoid edge clipping artifacts.
max_text_width = 8.6
max_lines_per_page = 4

shorts_output = "Quran_Shorts.mp4"

reciter = "ar.husary"
fade_in_ms = 200
fade_out_ms = 300

MAX_DURATION = 20
TEMP_AUDIO = "temp_check.mp3"
USED_FILE = "used_ayahs.json"

# ------------------- Manim Shorts Config (9:16) -------------------
# Render Manim directly in portrait (no intermediate landscape output).
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16
config.background_color = BLACK

# ------------------- حذف الصوت القديم -------------------
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

        except Exception as e:
            print(f"خطأ: {e}")
            continue

    raise Exception("❌ لم يتم العثور على آية قصيرة")

# ------------------- دمج الصوت -------------------
def combine_audios(files, output="audio.mp3"):
    combined = AudioSegment.empty()
    for f in files:
        combined += AudioSegment.from_mp3(f)
    combined = normalize(combined)
    combined = combined.fade_in(fade_in_ms).fade_out(fade_out_ms)
    combined.export(output, format="mp3")
    return output

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

    base = Rectangle(width=width, height=height, fill_color="#0b0b0b", fill_opacity=1)
    overlay = ImageMobject(rgba).set_height(height).set_width(width).set_opacity(0.25)
    vignette = Rectangle(width=width, height=height, fill_color=BLACK, fill_opacity=0.15)

    return Group(base, overlay, vignette)

# ------------------- المشهد -------------------
class QuranShortScene(Scene):
    def construct(self):
        bg = build_background()
        self.add(bg)

        surah, ayah, text = choose_short_ayah()
        audio_file = download_audio(surah, ayah, f"audio_{ayah}.mp3")

        audio_path = combine_audios([audio_file])
        audio_length = MP3(audio_path).info.length
        # Add audio directly in Manim to avoid ffmpeg post-processing (and any pad borders).
        self.add_sound(os.path.abspath(audio_path), time_offset=0)

        surah_name = get_surah_name(surah)
        ayah_label = to_arabic_indic_digits(str(ayah))

        wrapped_lines = split_text_manim(text, font_name, font_size_ayah, max_width=max_text_width)
        pages = [wrapped_lines[i:i+max_lines_per_page] for i in range(0, len(wrapped_lines), max_lines_per_page)]

        per_page = max(audio_length / len(pages), 2.0)

        for i, page in enumerate(pages, start=1):
            # Wrap chained calls in parentheses so line breaks are always valid Python.
            text_block = (
                MarkupText(
                    " ".join(page),
                    font=font_name,
                    font_size=font_size_ayah,
                )
                .align_to(RIGHT)
                .move_to(ORIGIN + UP * 0.5)
            )
            
            ayah_circle = ayah_number_circle(ayah_label).next_to(text_block, LEFT)

            self.play(FadeIn(text_block), FadeIn(ayah_circle))
            self.wait(per_page)
            self.play(FadeOut(text_block), FadeOut(ayah_circle))

# ------------------- التنفيذ -------------------
if __name__ == "__main__":
    # Render directly as a 1080x1920 (9:16) YouTube Shorts mp4.
    # No intermediate landscape video and no ffmpeg pad/scale filters (prevents border lines).
    subprocess.run(
        ["manim", "-qh", "-o", shorts_output, os.path.abspath(__file__), "QuranShortScene"],
        check=True,
    )

    logger.info("✅ تم إنتاج فيديو Shorts بتنسيق 9:16 بدون حواف أو خطوط بيضاء")
