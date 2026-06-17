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
import re  # 🌟 تم إضافة مكتبة re لإزالة التشكيل

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

# =========================================================================
# 🛠️ إعدادات التصدير المباشر لفيديو شورت نيون (9:16)
# =========================================================================
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0

# --- الإعدادات الفنية للتصميم ---
font_name = "Amiri"
wrap_width_chars = 30        
background_color = "#05070a"
reciter = "ar.abdulbasitmurattal"

shorts_output = "Quran_Neon_Shorts.mp4"
MAX_DURATION = 20
USED_FILE = "used_ayahs.json"
TEMP_AUDIO = "temp.mp3"

# ------------------- تحميل البيانات -------------------
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

# ------------------- معالجة الصوت -------------------
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

# ------------------- اختيار آية عشوائية ملائمة -------------------
def choose_random_ayah():
    used = load_used()
    candidates = []

    for s_idx, surah in enumerate(QURAN_DATA["data"]["surahs"], start=1):
        for a_idx, ayah in enumerate(surah["ayahs"], start=1):
            key = f"{s_idx}:{a_idx}"
            if key not in used:
                candidates.append((s_idx, a_idx, ayah["text"], surah["name"]))

    random.shuffle(candidates)

    for surah, ayah, text, surah_name in candidates:
        try:
            download_audio(surah, ayah, TEMP_AUDIO)
            duration = get_duration(TEMP_AUDIO)

            if duration <= MAX_DURATION:
                used.add(f"{surah}:{ayah}")
                save_used(used)
                os.remove(TEMP_AUDIO)
                return surah, ayah, text, surah_name

            os.remove(TEMP_AUDIO)
        except Exception:
            continue
    raise Exception("❌ لم يتم العثور على آية مناسبة للشورت")

# =========================================================================
# 🎬 مشهد الرسوم المتحركة
# =========================================================================
class QuranScene(Scene):
    def construct(self):
        # 1. إعداد الخلفية الداكنة العميقة
        self.camera.background_color = background_color
        bg_glow = FullScreenRectangle(
            fill_color=background_color,
            fill_opacity=1,
            stroke_width=0
        )
        bg_glow.stretch_to_fit_width(self.camera.frame_width)
        bg_glow.stretch_to_fit_height(self.camera.frame_height)
        self.add(bg_glow)

        # 2. جلب بيانات الآية عشوائياً
        surah_num, ayah_num, raw_text, surah_name = choose_random_ayah()
        
        # تنظيف وتحضير النص وحساب عدد الأسطر الناتجة
        raw_text = " ".join(raw_text.split())
        wrapped_lines = textwrap.wrap(raw_text, width=wrap_width_chars)
        num_lines = len(wrapped_lines)
        formatted_text = "\n".join(wrapped_lines)

        # تحميل وتجهيز الصوت
        audio_file = download_audio(surah_num, ayah_num, f"audio_{ayah_num}.mp3")
        audio_path = combine_audio([audio_file])
        audio_length = MP3(audio_path).info.length

        # ضبط حجم الخط ديناميكياً بقيم أكبر
        if num_lines <= 3:
            dynamic_font_size = 58
            line_space_factor = 1.4
            buff_distance = 0.6
        else:
            dynamic_font_size = max(42, 58 - (num_lines - 3) * 4) 
            line_space_factor = 1.25                                     
            buff_distance = 0.45                                  

        # 3. بناء مصفوفة النص والخطوط الزخرفية
        ayah_base = Text(
            formatted_text,
            font=font_name,
            font_size=dynamic_font_size,            
            line_spacing=line_space_factor,
            color=WHITE
        )
        
        card_width = config.frame_width * 0.95
        horizontal_padding = 1.4
        vertical_padding = 1.3

        if ayah_base.width > card_width - horizontal_padding:
            ayah_base.scale_to_fit_width(card_width - horizontal_padding)

        text_group = ayah_base

        glass = RoundedRectangle(
            width=card_width,
            height=text_group.height + vertical_padding,
            corner_radius=0.45,
        )
        
        glass.set_fill(color="#0b1018", opacity=0.65)
        glass.set_stroke(color=WHITE, width=1.4, opacity=0.35)
        glass.move_to(ayah_base.get_center())

        ayah_base.move_to(glass.get_center())

        # 🌟 إزالة التشكيل (الحركات) والزخارف من اسم السورة 🌟
        clean_surah_name = re.sub(r'[\u064B-\u0652]', '', surah_name).strip()
        
        if clean_surah_name.startswith("سورة"):
            clean_surah_name = clean_surah_name.removeprefix("سورة").strip()

        surah_info = Text(
            f"سورة {clean_surah_name} • الآية {ayah_num}", 
            font="Almarai", 
            font_size=24, 
            color=GRAY_B, 
            fill_opacity=0.75
        )
        surah_info.next_to(glass, DOWN, buff=0.55)

        display_group = VGroup(glass, ayah_base, surah_info)
        display_group.move_to(UP * 0.25)

        fade_in_time = 1.2
        fade_out_time = 1.0
        recitation_time = max(1.0, audio_length - fade_in_time - fade_out_time)

        self.play(
            FadeIn(display_group, shift=UP * 0.15),
            run_time=fade_in_time,
            rate_func=smooth
        )

        self.play(
            display_group.animate.scale(1.03),
            run_time=recitation_time,
            rate_func=linear
        )

        self.play(
            FadeOut(display_group),
            run_time=fade_out_time,
            rate_func=smooth
        )

        self.wait(0.4)

# =========================================================================
# 🚀 تشغيل دمج الفيديو التلقائي والصوت عبر FFmpeg
# =========================================================================
if __name__ == "__main__":
    subprocess.run(
        ["manim", "-qh", os.path.abspath(__file__), "QuranScene"],
        check=True
    )

    generated_video = glob.glob("media/videos/**/*QuranScene.mp4", recursive=True)[0]

    subprocess.run([
        "ffmpeg", "-y",
        "-i", generated_video,
        "-i", "audio.mp3",
        "-c:v", "copy",        
        "-c:a", "aac",
        "-shortest",
        shorts_output,
    ], check=True)

    for f in glob.glob("audio_*.mp3"):
        try: os.remove(f)
        except: pass

    logger.info(f"🎉 تم بنجاح تصدير فيديو الشورت النيوني: {shorts_output}")
