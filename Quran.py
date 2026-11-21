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
background_color = "#F2FFF7"
text_color = "#1B5E20"
pattern_color = "#2E7D32"
info_color = "#5F6962"
brand_name = "نسمات القرآن"
reciter = "ar.husary"
shorts_output = "Quran_Shorts.mp4"
# Prefer complete, longer verses while keeping each Short concise.
MIN_AYAH_CHARACTERS = 100
MIN_DURATION = 8
MAX_DURATION = 25
USED_FILE = "used_ayahs.json"
TEMP_AUDIO = "temp.mp3"

# Visual themes. The original green design remains available, alongside
# several distinct palettes suitable for producing alternate versions.
STYLE_PRESETS = {
    "green": {"name": "الأخضر الإسلامي", "top": "#F2FFF7", "bottom": "#FFFFFF", "text": "#1B5E20", "accent": "#2E7D32", "info": "#5F6962", "gold": "#B89A55", "glow": "#2E7D32"},
    "midnight": {"name": "الأزرق الليلي", "top": "#081A33", "bottom": "#142D4E", "text": "#F3F7FF", "accent": "#75B9F2", "info": "#C5D4E8", "gold": "#E6C77A", "glow": "#75B9F2"},
    "royal": {"name": "البنفسجي الملكي", "top": "#211333", "bottom": "#43265D", "text": "#FFF7FF", "accent": "#D6A7F0", "info": "#E2D2EA", "gold": "#F0CF83", "glow": "#C58BE8"},
    "ocean": {"name": "المحيط الفيروزي", "top": "#E8FAFC", "bottom": "#C9EEF1", "text": "#064B59", "accent": "#087E8B", "info": "#426A70", "gold": "#B78A43", "glow": "#39A8B5"},
    "sand": {"name": "الذهبي الصحراوي", "top": "#FFF8E8", "bottom": "#EEDDBB", "text": "#513B20", "accent": "#9B7135", "info": "#76664F", "gold": "#B18A45", "glow": "#C49A50"},
    "slate": {"name": "الرمادي الفاخر", "top": "#202833", "bottom": "#394653", "text": "#F4F1E8", "accent": "#B7C5D4", "info": "#D1D8DF", "gold": "#D6B56D", "glow": "#9EADBC"},
}

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


def choose_random_ayah():
    global VIDEO_TITLE
    used = load_used()
    candidates = []

    for s_idx, surah in enumerate(QURAN_DATA["data"]["surahs"], start=1):
        for a_idx, ayah in enumerate(surah["ayahs"], start=1):
            key = f"{s_idx}:{a_idx}"
            verse_text = " ".join(ayah["text"].split())
            if key not in used and len(verse_text) >= MIN_AYAH_CHARACTERS:
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


def build_background(style=None):
    """Build a vertical gradient using the selected visual theme."""
    style = style or STYLE_PRESETS["green"]
    pixel_h, pixel_w = config.pixel_height, config.pixel_width
    top = np.array(color_to_rgb(style["top"]), dtype=np.float32) * 255
    bottom = np.array(color_to_rgb(style["bottom"]), dtype=np.float32) * 255
    blend = np.linspace(0.0, 1.0, pixel_h, dtype=np.float32)[:, None, None]
    rows = top[None, None, :] * (1.0 - blend) + bottom[None, None, :] * blend
    rgb = np.broadcast_to(rows, (pixel_h, pixel_w, 3)).astype(np.uint8).copy()
    return ImageMobject(rgb).set(height=config.frame_height, width=config.frame_width)


def decorative_motif(style=None, motif_key=None):
    """Create a distinct geometric Islamic background ornament for each video."""
    style = style or STYLE_PRESETS["green"]
    motif_key = motif_key or "rosette"
    gold = style["gold"]

    if motif_key == "rosette":
        petals = VGroup(*[
            Circle(radius=0.78).move_to(0.78 * np.array([np.cos(TAU * i / 8), np.sin(TAU * i / 8), 0]))
            for i in range(8)
        ])
        motif = VGroup(Circle(radius=0.82), petals, Circle(radius=1.62), Circle(radius=1.78))
    elif motif_key == "eight_point_star":
        motif = VGroup(
            RegularPolygon(n=8).scale(1.75),
            Square(side_length=2.45).rotate(PI / 4),
            Square(side_length=2.45),
            Circle(radius=0.58),
        )
    elif motif_key == "nested_medallion":
        motif = VGroup(
            Circle(radius=1.8), Circle(radius=1.55),
            RegularPolygon(n=12).scale(1.35),
            RegularPolygon(n=6).scale(0.95),
            RegularPolygon(n=6).scale(0.62).rotate(PI / 6),
        )
    elif motif_key == "diamond_lattice":
        diamonds = VGroup(*[
            Square(side_length=0.78).rotate(PI / 4).move_to([x, y, 0])
            for x in (-1.05, 0, 1.05) for y in (-1.05, 0, 1.05)
        ])
        motif = VGroup(diamonds, Square(side_length=3.25).rotate(PI / 4))
    elif motif_key == "flower":
        petals = VGroup(*[
            Ellipse(width=0.72, height=1.35).move_to(0.68 * np.array([np.cos(TAU * i / 8), np.sin(TAU * i / 8), 0])).rotate(TAU * i / 8)
            for i in range(8)
        ])
        motif = VGroup(petals, Circle(radius=0.42), Circle(radius=1.55))
    else:  # archwork
        arches = VGroup(*[
            Arc(radius=radius, start_angle=0, angle=PI, arc_center=ORIGIN).shift(DOWN * 0.15)
            for radius in (0.75, 1.05, 1.35, 1.65)
        ])
        motif = VGroup(arches, Line(LEFT * 1.7, RIGHT * 1.7).shift(DOWN * 0.15))

    motif.set_color(style["accent"])
    motif.set_stroke(width=2.0)
    motif.set_opacity(0.19)
    motif.set(width=4.15)
    motif.move_to(ORIGIN)
    motif.add_updater(lambda mob, dt: mob.rotate(TAU * 0.05 * dt))
    return motif


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
    """Wrap the complete Arabic ayah without ever splitting or dropping a word."""
    normalized = " ".join(text.split())
    if not normalized:
        return []

    max_width = config.frame_width - 1.0
    words = normalized.split(" ")
    lines = []
    current_line = ""

    for word in words:
        candidate = f"{current_line} {word}".strip()
        candidate_mobject = Text(candidate, font=font_name, font_size=66)

        if current_line and candidate_mobject.width > max_width:
            lines.append(current_line)
            current_line = word
        else:
            current_line = candidate

    if current_line:
        lines.append(current_line)

    # Safety check: the words and their order must remain exactly as supplied.
    if " ".join(lines).split() != normalized.split():
        raise ValueError("حدث اختلاف أثناء تنسيق الآية؛ تم إيقاف إنشاء الفيديو لمنع فقدان أي كلمة.")

    return lines


def paginate(lines: list[str]) -> list[list[str]]:
    return [lines[i:i + max_lines_per_page] for i in range(0, len(lines), max_lines_per_page)]


def make_block(lines: list[str], style=None) -> VGroup:
    style = style or STYLE_PRESETS["green"]
    texts = [Text(line, font=font_name, font_size=66, color=style["text"]) for line in lines]
    return VGroup(*texts).arrange(DOWN, buff=0.32).move_to(ORIGIN)


def corner_ornament(x: float, y: float, flip_x: float, flip_y: float) -> VGroup:
    """Fine geometric corner detail, kept well outside the verse area."""
    gold = "#b89a55"
    horizontal = Line(ORIGIN, RIGHT * 1.0, color=gold, stroke_width=1.2).move_to([x + flip_x * 0.5, y, 0])
    vertical = Line(ORIGIN, DOWN * 1.0, color=gold, stroke_width=1.2).move_to([x, y - flip_y * 0.5, 0])
    diamond = Square(side_length=0.2, color=gold, stroke_width=1.1, fill_opacity=0)
    diamond.rotate(PI / 4).move_to([x + flip_x * 0.22, y - flip_y * 0.22, 0])
    dot = Dot([x + flip_x * 0.58, y - flip_y * 0.58, 0], radius=0.025, color=gold)
    return VGroup(horizontal, vertical, diamond, dot).set_opacity(0.58)


class QuranScene(Scene):
    def construct(self):
        style_key = os.environ.get("QURAN_STYLE", "green")
        style = STYLE_PRESETS.get(style_key, STYLE_PRESETS["green"])
        self.camera.background_color = style["top"]
        self.add(build_background(style))

        motif_key = os.environ.get("QURAN_MOTIF", "rosette")
        motif = decorative_motif(style, motif_key)
        self.add(motif)

        # Both output versions read the same selected ayah, so only the design changes.
        if os.path.exists("selected_ayah.json"):
            with open("selected_ayah.json", "r", encoding="utf-8") as selected_file:
                selected = json.load(selected_file)
            surah, ayah, text = selected["surah"], selected["ayah"], selected["text"]
        else:
            surah, ayah, text, _ = choose_random_ayah()
        surah_name = get_surah_name(surah)
        ayah_label = to_arabic_indic_digits(str(ayah))

        audio_file = download_audio(surah, ayah, f"audio_{surah}_{ayah}.mp3")
        with open("selected_audio.txt", "w", encoding="utf-8") as selected_file:
            selected_file.write(audio_file)
        audio_length = MP3(audio_file).info.length

        wrapped_lines = wrap_text(text)
        block = make_block(wrapped_lines, style)

        # Verify that the rendered lines contain every word from the source ayah.
        source_words = " ".join(text.split()).split()
        rendered_words = " ".join(wrapped_lines).split()
        if rendered_words != source_words:
            raise ValueError("الآية المعروضة لا تطابق النص الأصلي؛ تم إيقاف التصدير لتجنب حذف الكلمات.")

        max_text_width = config.frame_width - 1.0
        max_text_height = config.frame_height - 6.0
        block.scale(min(1.0, max_text_width / block.width, max_text_height / block.height))
        block.move_to(ORIGIN + DOWN * 0.1)

        surah_title = Text(surah_name, font=font_name, font_size=46, color=style["text"])
        ayah_ref = Text(f"آية {ayah_label}", font=font_name, font_size=30, color=style["accent"])
        heading = VGroup(surah_title, ayah_ref).arrange(DOWN, buff=0.18)
        heading.move_to(UP * (config.frame_height / 2 - 2.1))
        divider = Line(LEFT * 0.55, RIGHT * 0.55, color=style["gold"], stroke_width=1.8)
        divider.next_to(heading, DOWN, buff=0.48)
        footer = Text(
            brand_name, font=font_name, font_size=30, color=style["info"]
        ).move_to(DOWN * (config.frame_height / 2 - 1.45))

        glow = VGroup(*[
            Circle(radius=1.5 + index * 0.7, stroke_width=0, fill_color=style["glow"], fill_opacity=0.010)
            for index in range(5)
        ]).move_to(block.get_center())
        self.add(glow)
        entrance_duration = min(0.8, max(0.2, audio_length * 0.15))
        self.play(
            FadeIn(heading, shift=DOWN * 0.12), FadeIn(divider),
            FadeIn(block, shift=UP * 0.12), FadeIn(footer),
            run_time=entrance_duration, rate_func=smooth,
        )
        # Keep every word visible and motionless for the whole recitation.
        self.wait(max(0.1, audio_length - entrance_duration) + 0.1)
        motif.clear_updaters()


def render_one(output_path: str):
    """Render one video using QURAN_STYLE (or the original green theme)."""
    style_key = os.environ.get("QURAN_STYLE", "green")
    scene_name = f"QuranScene_{style_key}"
    subprocess.run(["manim", "-qh", os.path.abspath(__file__), "QuranScene", "-o", scene_name], check=True)

    matches = glob.glob(f"media/videos/**/*{scene_name}.mp4", recursive=True)
    if not matches:
        raise FileNotFoundError(f"لم يتم العثور على فيديو Manim الناتج للنمط {style_key}")
    video = max(matches, key=os.path.getmtime)
    with open("selected_audio.txt", "r", encoding="utf-8") as selected_file:
        selected_audio_file = selected_file.read().strip()
    subprocess.run([
        "ffmpeg", "-y", "-i", video, "-i", selected_audio_file,
        "-vf", "scale=1080:1920", "-c:v", "libx264", "-c:a", "copy",
        "-shortest", output_path,
    ], check=True)
    logger.info("✅ تم إنتاج الفيديو: %s", output_path)


def render_two_variants():
    """Choose a different ayah and a different theme for each of the two videos."""
    non_green_styles = [key for key in STYLE_PRESETS if key != "green"]
    chosen_styles = random.sample(non_green_styles, 2)
    motif_keys = ["rosette", "eight_point_star", "nested_medallion", "diamond_lattice", "flower", "archwork"]
    chosen_motifs = random.sample(motif_keys, 2)

    for index, style_key in enumerate(chosen_styles, start=1):
        # A new ayah for each video
        surah, ayah, text, _ = choose_random_ayah()
        with open("selected_ayah.json", "w", encoding="utf-8") as selected_file:
            json.dump({"surah": surah, "ayah": ayah, "text": text}, selected_file, ensure_ascii=False, indent=2)

        motif_key = chosen_motifs[index - 1]
        logger.info("🎨 الفيديو %d: آية %s:%s، النمط %s، الزخرفة %s", index, surah, ayah, STYLE_PRESETS[style_key]["name"], motif_key)

        env = os.environ.copy()
        env["QURAN_STYLE"] = style_key
        env["QURAN_MOTIF"] = motif_key
        scene_name = f"QuranScene_{style_key}_{motif_key}"
        subprocess.run(["manim", "-qh", os.path.abspath(__file__), "QuranScene", "-o", scene_name], check=True, env=env)

        matches = glob.glob(f"media/videos/**/*{scene_name}.mp4", recursive=True)
        if not matches:
            raise FileNotFoundError(f"لم يتم العثور على فيديو النمط {style_key}")
        video = max(matches, key=os.path.getmtime)
        audio_file = f"audio_{surah}_{ayah}.mp3"
        output_path = f"Quran_{index}_{style_key}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-i", video, "-i", audio_file,
            "-vf", "scale=1080:1920", "-c:v", "libx264", "-c:a", "copy",
            "-shortest", output_path,
        ], check=True)
        logger.info("✅ تم إنتاج الفيديو %s", output_path)
        # Telegram notification remains optional; it never blocks a successful export.
        try:
            from bot import notify_exported
            notify_exported(
                surah_name=get_surah_name(surah),
                surah=surah,
                ayah=ayah,
                text=text,
                duration=MP3(audio_file).info.length,
                output_path=output_path,
            )
        except Exception as exc:
            logger.warning("⚠️ تعذر إرسال إشعار Telegram، لكن الفيديو تم تصديره بنجاح: %s", exc)

    logger.info("🎉 اكتمل إنتاج نسختين مختلفتين للآية نفسها.")


if __name__ == "__main__":
    if os.environ.get("RENDER_TWO", "1") == "1":
        render_two_variants()
    else:
        render_one(os.environ.get("OUTPUT_FILE", shorts_output))
