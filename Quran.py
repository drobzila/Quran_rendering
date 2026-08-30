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

config.frame_width = 9
config.frame_height = 16
config.pixel_width = 1080
config.pixel_height = 1920

VIDEO_TITLE = ""

FALLBACK_TITLES = [
    "تلاوة قرآنية مؤثرة 🌿",
    "راحة نفسية مع القرآن الكريم",
    "آيات تريح القلب 🤍",
    "استمع لكلام الله بخشوع",
    "تلاوة هادئة للقلب والروح",
    "القرآن الكريم بصوت جميل",
    "آيات من القرآن الكريم",
    "تلاوة قصيرة ومؤثرة",
    "سكينة وطمأنينة مع القرآن",
    "أجمل التلاوات القرآنية",
    "دقيقة من الجمال القرآني",
    "تلاوة تلامس القلب",
    "نور القرآن الكريم ✨",
    "كلام الله يريح القلوب",
    "استمع وتدبر آيات الله",
]

font_name = "Amiri"
font_size_ayah = 72
wrap_width_chars = 42
max_lines_per_page = 5
line_spacing = 0.5
background_color = "#0b0f1a"
text_color = WHITE
reciter = "ar.husary"
shorts_output = "Quran_Shorts.mp4"
MIN_DURATION = 4
MAX_DURATION = 20
USED_FILE = "used_ayahs.json"
TEMP_AUDIO = "temp.mp3"

with open("quran.json", "r", encoding="utf-8") as f:
    QURAN_DATA = json.load(f)


def load_used():
    if os.path.exists(USED_FILE):
        with open(USED_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_used(data):
    with open(USED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(data), f, ensure_ascii=False, indent=2)


def download_audio(surah: int, ayah: int, filename: str) -> str:
    url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/{reciter}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()
    audio_url = data["data"]["audio"]
    audio_response = requests.get(audio_url, timeout=20)
    audio_response.raise_for_status()
    with open(filename, "wb") as f:
        f.write(audio_response.content)
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


def choose_random_ayah():
    global VIDEO_TITLE
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

            if not (MIN_DURATION <= duration <= MAX_DURATION):
                os.remove(TEMP_AUDIO)
                continue

            used.add(f"{surah}:{ayah}")
            save_used(used)
            os.remove(TEMP_AUDIO)

            VIDEO_TITLE = text.strip().replace("\n", " ").replace("\r", " ")
            if not VIDEO_TITLE or len(VIDEO_TITLE) > 90:
                VIDEO_TITLE = random.choice(FALLBACK_TITLES)

            with open("title.txt", "w", encoding="utf-8") as f:
                f.write(VIDEO_TITLE.strip())

            return surah, ayah, text, duration

        except Exception as exc:
            logger.warning("تعذر معالجة الآية %s:%s: %s", surah, ayah, exc)
            if os.path.exists(TEMP_AUDIO):
                try:
                    os.remove(TEMP_AUDIO)
                except OSError:
                    pass
            continue

    raise Exception("❌ لم يتم العثور على آية مناسبة")


import numpy as np


def build_background():
    width = config.frame_width
    height = config.frame_height
    h, w = 1920, 1080
    noise = np.random.normal(loc=0.0, scale=1.0, size=(h, w)).astype(np.float32)
    noise = (noise - noise.min()) / (noise.max() - noise.min() + 1e-8)
    rgb = (noise * 12).astype(np.uint8)
    rgba = np.stack([rgb, rgb, rgb, np.full_like(rgb, 16, dtype=np.uint8)], axis=-1)
    base = Rectangle(width=width, height=height, fill_color=background_color, fill_opacity=1, stroke_width=0)
    overlay = ImageMobject(rgba).set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    overlay.set(height=height, width=width)
    overlay.set_opacity(0.25)
    vignette = Rectangle(width=width, height=height, fill_color=BLACK, fill_opacity=0.2, stroke_width=0)
    return Group(base, overlay, vignette)


def decorative_divider(width=2.0):
    return Line(LEFT * (width / 2), RIGHT * (width / 2), stroke_color=GOLD, stroke_width=1.5)


def get_surah_name(surah: int) -> str:
    return QURAN_DATA["data"]["surahs"][surah - 1]["name"]


def to_arabic_indic_digits(value) -> str:
    return str(value).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))


def ayah_number_circle(number: str) -> VGroup:
    circle = Circle(radius=0.35, color=GOLD, stroke_width=3)
    number_text = Text(number, font=font_name, font_size=28, color=GOLD)
    number_text.move_to(circle.get_center())
    return VGroup(circle, number_text)


def progress_bar(total_width=None, y=None) -> Line:
    total_width = total_width or (config.frame_width - 0.4)
    y = y if y is not None else -(config.frame_height / 2 - 0.5)
    track = Line(LEFT * (total_width / 2), RIGHT * (total_width / 2), stroke_color=GRAY_E, stroke_width=6)
    track.move_to([0, y, 0])
    return track


def wrap_text(text: str) -> list[str]:
    return textwrap.wrap(" ".join(text.split()), width=wrap_width_chars)


def paginate(lines: list[str]) -> list[list[str]]:
    return [lines[i:i + max_lines_per_page] for i in range(0, len(lines), max_lines_per_page)]


def make_block(lines: list[str]) -> VGroup:
    texts = [Text(line, font=font_name, font_size=font_size_ayah, color=text_color) for line in lines]
    return VGroup(*texts).arrange(DOWN, buff=line_spacing).move_to(ORIGIN)


class QuranScene(Scene):
    def construct(self):
        self.camera.background_color = background_color
        self.add(build_background())

        surah, ayah, text, _ = choose_random_ayah()
        surah_name = get_surah_name(surah)
        ayah_label = to_arabic_indic_digits(str(ayah))

        audio_file = download_audio(surah, ayah, f"audio_{surah}_{ayah}.mp3")
        audio_path = combine_audio([audio_file])
        audio_length = MP3(audio_path).info.length

        lines = wrap_text(text)
        pages = paginate(lines)

        surah_title = Text(surah_name, font=font_name, font_size=90, color=WHITE)
        ayah_ref = Text(f"آية {ayah_label}", font=font_name, font_size=42, color=GRAY_B)
        intro = VGroup(surah_title, ayah_ref).arrange(DOWN, buff=0.4).move_to(ORIGIN)
        self.play(FadeIn(intro, scale=0.92), run_time=0.6, rate_func=smooth)
        self.wait(0.35)
        self.play(FadeOut(intro, scale=1.05), run_time=0.4, rate_func=smooth)

        per_page = max(audio_length / len(pages), 2.5)
        track = progress_bar()
        tracker = ValueTracker(0.0)
        fill = always_redraw(lambda: Line(
            track.get_start(),
            track.get_start() + RIGHT * (track.get_length() * tracker.get_value()),
            stroke_color=GOLD,
            stroke_width=6,
        ))
        self.add(VGroup(track, fill))

        for page_index, page in enumerate(pages, start=1):
            block = make_block(page)
            plate = RoundedRectangle(
                corner_radius=0.3,
                width=min(block.width + 1.2, config.frame_width - 0.4),
                height=min(block.height + 1.0, config.frame_height - 4.0),
                stroke_width=1,
                stroke_color=GOLD_E,
                stroke_opacity=0.4,
                fill_color=BLACK,
                fill_opacity=0.35,
            ).move_to(block.get_center())

            ayah_circle = ayah_number_circle(ayah_label)
            ayah_circle.next_to(block, UP, buff=0.4)
            glow = Circle(radius=0.42, color=GOLD, stroke_width=1, stroke_opacity=0.3, fill_opacity=0)
            glow.move_to(ayah_circle.get_center())

            info_text = Text(
                f"{surah_name} ({to_arabic_indic_digits(str(surah))})",
                font=font_name,
                font_size=32,
                color=GRAY,
            ).next_to(block, DOWN, buff=0.8)
            page_text = Text(
                f"{to_arabic_indic_digits(str(page_index))}/{to_arabic_indic_digits(str(len(pages)))}",
                font=font_name,
                font_size=26,
                color=GRAY_B,
            ).to_edge(DOWN, buff=0.9)

            self.play(
                FadeIn(plate), FadeIn(block, scale=0.94), FadeIn(ayah_circle, scale=0.8),
                FadeIn(glow, scale=0.7), FadeIn(info_text), FadeIn(page_text),
                run_time=1, rate_func=smooth,
            )
            self.play(tracker.animate.set_value(page_index / len(pages)), run_time=per_page - 1, rate_func=linear)
            self.play(
                FadeOut(block, scale=1.03), FadeOut(plate), FadeOut(ayah_circle),
                FadeOut(glow), FadeOut(info_text), FadeOut(page_text),
                run_time=0.7, rate_func=smooth,
            )


def render_one(output_path: str):
    global shorts_output
    shorts_output = output_path

    subprocess.run(["manim", "-qh", os.path.abspath(__file__), "QuranScene"], check=True)

    video = glob.glob("media/videos/**/*QuranScene.mp4", recursive=True)[0]
    intro_delay = 1.2
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video,
        "-itsoffset", str(intro_delay),
        "-i", "audio.mp3",
        "-vf", "scale=1080:1920",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        output_path,
    ], check=True)

    logger.info(f"✅ تم إنتاج الفيديو: {output_path}")

    # Telegram إشعار فقط، وليس خطوة مطلوبة لإكمال الرندر.
    try:
        from bot import notify_exported

        audio_files = glob.glob("audio_*.mp3")
        selected_audio = max(audio_files, key=os.path.getmtime) if audio_files else None
        surah = ayah = None
        if selected_audio:
            stem = os.path.splitext(os.path.basename(selected_audio))[0]
            parts = stem.split("_")
            if len(parts) == 3:
                surah, ayah = int(parts[1]), int(parts[2])

        text = ""
        if os.path.exists("title.txt"):
            with open("title.txt", "r", encoding="utf-8") as f:
                text = f.read().strip()

        if surah is not None and ayah is not None:
            notify_exported(
                surah_name=get_surah_name(surah),
                surah=surah,
                ayah=ayah,
                text=text,
                duration=MP3(selected_audio).info.length if selected_audio else 0,
                output_path=output_path,
            )
    except Exception as exc:
        logger.warning("⚠️ تعذر إرسال إشعار Telegram، لكن الفيديو تم تصديره بنجاح: %s", exc)


if __name__ == "__main__":
    render_one(os.environ.get("OUTPUT_FILE", shorts_output))
