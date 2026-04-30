from manim import *
import logging
import shlex
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

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ------------------- إعدادات -------------------
surah_number = 16
start_ayah = 107
end_ayah = 107

font_name = "Amiri"
font_size_ayah = 60
max_text_width = 9.2
max_lines_per_page = 4

normal_output = "Quran_Normal.mp4"
shorts_output = "Quran_Shorts.mp4"

reciter = "ar.husary"
auto_confirm = False
fade_in_ms = 200
fade_out_ms = 300

# ------------------- حذف الصوت -------------------
for f in glob.glob("audio*.mp3"):
    os.remove(f)

# ------------------- تحميل البيانات -------------------
with open("quran.json", "r", encoding="utf-8") as f:
    QURAN_DATA = json.load(f)

def get_ayah_text(surah, ayah):
    return QURAN_DATA["data"]["surahs"][surah - 1]["ayahs"][ayah - 1]["text"]

def get_surah_name(surah):
    return QURAN_DATA["data"]["surahs"][surah - 1]["name"]

# ------------------- تحميل الصوت -------------------
def download_audio(surah, ayah, filename):
    url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/{reciter}"
    r = requests.get(url, timeout=20).json()
    audio_url = r["data"]["audio"]
    audio_data = requests.get(audio_url, timeout=20).content
    with open(filename, "wb") as f:
        f.write(audio_data)
    return filename
  requests.get(audio_url, timeout=30)

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
    if not words:
        return []
    lines = []
    current = []

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
    # Subtle noise overlay to avoid a flat background.
    h, w = 1920, 1080
    noise = np.random.normal(loc=0.0, scale=1.0, size=(h, w)).astype(np.float32)
    noise = (noise - noise.min()) / (noise.max() - noise.min() + 1e-8)
    rgb = (noise * 14).astype(np.uint8)  # keep it very dark
    rgba = np.stack([rgb, rgb, rgb, np.full_like(rgb, 18, dtype=np.uint8)], axis=-1)

    base = Rectangle(width=width, height=height, fill_color="#0b0b0b", fill_opacity=1, stroke_width=0)
    overlay = ImageMobject(rgba).set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    overlay.set_height(height)
    overlay.set_width(width)
    overlay.set_opacity(0.25)

    vignette = Rectangle(width=width, height=height, fill_color=BLACK, fill_opacity=0.15, stroke_width=0)
    # ImageMobject is not a VMobject, so it cannot live in VGroup.
    return Group(base, overlay, vignette)

def progress_bar(total_width=8.6, y=-6.9):
    track = Line(
        LEFT * (total_width / 2),
        RIGHT * (total_width / 2),
        stroke_color=GRAY_E,
        stroke_width=6,
    )
    track.move_to([0, y, 0])
    return track

# ------------------- المشهد -------------------
class QuranShortScene(Scene):
    def construct(self):
        bg = build_background()
        self.add(bg)

        texts = []
        audio_files = []

        for ayah in range(start_ayah, end_ayah + 1):
            text = get_ayah_text(surah_number, ayah)
            audio_file = download_audio(surah_number, ayah, f"audio_{ayah}.mp3")

            texts.append((text, ayah))
            audio_files.append(audio_file)

        audio_path = combine_audios(audio_files)

        audio_length = MP3(audio_path).info.length
        surah_name = get_surah_name(surah_number)

        full_text = " ".join([t[0] for t in texts])

        wrapped_lines = split_text_manim(full_text, font_name, font_size_ayah, max_width=max_text_width)

        pages = [
            wrapped_lines[i : i + max_lines_per_page]
            for i in range(0, len(wrapped_lines), max_lines_per_page)
        ]
        if not pages:
            logger.error("No pages generated; check text wrapping parameters")
            return

        if start_ayah == end_ayah:
            ayah_label = to_arabic_indic_digits(str(end_ayah))
        else:
            ayah_label = (
                f"{to_arabic_indic_digits(str(start_ayah))}-"
                f"{to_arabic_indic_digits(str(end_ayah))}"
            )

        # Quick intro (keeps hook on the ayah, no long title card)
        intro = VGroup(
            Text(surah_name, font=font_name, font_size=52, color=WHITE),
            Text(f"آية {ayah_label}", font=font_name, font_size=34, color=GRAY_B),
        ).arrange(DOWN, buff=0.25).to_edge(UP, buff=1.0)
        self.play(FadeIn(intro, shift=UP * 0.2), run_time=0.5)
        self.wait(0.35)
        self.play(FadeOut(intro, shift=UP * 0.2), run_time=0.35)

        per_page = max(audio_length / len(pages), 2.0)
        track = progress_bar()

        for page_index, page in enumerate(pages, start=1):
            # ------------------- النص -------------------
            text_lines = [
                MarkupText(line, font=font_name, font_size=font_size_ayah, color=WHITE)
                for line in page
            ]

            text_block = VGroup(*text_lines).arrange(DOWN, buff=0.45, aligned_edge=RIGHT)
            text_block.to_edge(RIGHT, buff=1.0)
            text_block.shift(UP * 0.6)

            plate = RoundedRectangle(
                corner_radius=0.25,
                width=min(text_block.width + 1.0, 10.2),
                height=min(text_block.height + 0.8, 7.0),
                stroke_width=0,
                fill_color=BLACK,
                fill_opacity=0.35,
            ).move_to(text_block.get_center())

            # ------------------- رقم الآية -------------------
            ayah_circle = ayah_number_circle(ayah_label)
            ayah_circle.next_to(text_block, LEFT, buff=0.55)
            ayah_circle.align_to(text_block, UP)

            # ------------------- اسم السورة -------------------
            info_text = Text(
                f"{surah_name} ({to_arabic_indic_digits(str(surah_number))})",
                font=font_name,
                font_size=32,
                color=GRAY
            )

            info_text.next_to(text_block, DOWN, buff=0.8)
            info_text.align_to(text_block, RIGHT)

            page_text = Text(
                f"{to_arabic_indic_digits(str(page_index))}/{to_arabic_indic_digits(str(len(pages)))}",
                font=font_name,
                font_size=26,
                color=GRAY_B,
            ).to_edge(DOWN, buff=0.7).to_edge(RIGHT, buff=1.0)

            # ------------------- أنيميشن احترافي -------------------
            tracker = ValueTracker(0.0)
            fill = always_redraw(
                lambda: Line(
                    track.get_start(),
                    track.get_start() + RIGHT * (track.get_length() * tracker.get_value()),
                    stroke_color=GOLD,
                    stroke_width=6,
                )
            )
            bar = VGroup(track, fill)
            self.add(bar)
            self.play(
                FadeIn(plate),
                LaggedStart(*[
                    FadeIn(line, shift=UP * 0.3)
                    for line in text_block
                ], lag_ratio=0.2),
                FadeIn(ayah_circle, scale=0.8),
                FadeIn(info_text),
                FadeIn(page_text),
                run_time=1.0
            )

            self.play(tracker.animate.set_value(1.0), run_time=per_page, rate_func=linear)

            self.play(
                FadeOut(text_block, shift=DOWN),
                FadeOut(ayah_circle),
                FadeOut(info_text),
                FadeOut(page_text),
                FadeOut(plate),
                FadeOut(bar),
                run_time=0.6
            )

# ------------------- التنفيذ -------------------
if __name__ == "__main__":
    subprocess.run(["manim", "-qh", os.path.abspath(__file__), "QuranShortScene"], check=True)

    video_files = sorted(glob.glob("media/videos/**/*.mp4", recursive=True))
    if not video_files:
        raise SystemExit("Rendered scene not found under media/videos")
    base_video = video_files[0]

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", base_video,
            "-i", "audio.mp3",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            normal_output,
        ],
        check=True,
    )

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", normal_output,
            "-vf",
            "scale=1080:1920:force_original_aspect_ratio=decrease,"
            "pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            "-c:a", "copy",
            shorts_output,
        ],
        check=True,
    )

    logger.info("✅ تم الإنتاج بنجاح")
