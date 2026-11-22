from __future__ import annotations
import json
import os
from manim import *
from mutagen.mp3 import MP3
from .audio import download_audio
from .config import BRAND_NAME, FONT_NAME, SELECTED_AYAH_FILE, SELECTED_AUDIO_FILE, STYLE_PRESETS, MAX_LINES_PER_PAGE
from .data import get_surah_name, to_arabic_indic_digits
from .selection import choose_random_ayah
from .visuals import build_background, decorative_motif, decorative_frame

def wrap_text(text: str) -> list[str]:
    """Wrap the complete ayah without splitting, reordering, or dropping words."""
    normalized = " ".join(text.split())
    if not normalized: return []
    max_width = config.frame_width - 1.0
    lines, current = [], ""
    for word in normalized.split(" "):
        candidate = f"{current} {word}".strip()
        measured = Text(candidate, font=FONT_NAME, font_size=66)
        if current and measured.width > max_width:
            lines.append(current); current = word
        else: current = candidate
    if current: lines.append(current)
    if " ".join(lines).split() != normalized.split():
        raise ValueError("حدث اختلاف أثناء تنسيق الآية؛ تم إيقاف إنشاء الفيديو لمنع فقدان أي كلمة.")
    return lines

def paginate(lines: list[str]) -> list[list[str]]:
    return [lines[i:i+MAX_LINES_PER_PAGE] for i in range(0,len(lines),MAX_LINES_PER_PAGE)]

def make_block(lines: list[str], style=None) -> VGroup:
    style = style or STYLE_PRESETS["green"]
    texts = [Text(line,font=FONT_NAME,font_size=66,color=style["text"]) for line in lines]
    return VGroup(*texts).arrange(DOWN,buff=.32).move_to(ORIGIN)

class QuranScene(Scene):
    def construct(self):
        style_key = os.environ.get("QURAN_STYLE","green")
        style = STYLE_PRESETS.get(style_key,STYLE_PRESETS["green"])
        self.camera.background_color = style["top"]
        self.add(build_background(style))\n        self.add(decorative_frame(style))
        motif = decorative_motif(style,os.environ.get("QURAN_MOTIF","rosette"))
        self.add(motif)
        if SELECTED_AYAH_FILE.exists():
            selected = json.loads(SELECTED_AYAH_FILE.read_text(encoding="utf-8"))
            surah,ayah,text = selected["surah"],selected["ayah"],selected["text"]
        else:
            surah,ayah,text,_ = choose_random_ayah()
            SELECTED_AYAH_FILE.write_text(json.dumps({"surah":surah,"ayah":ayah,"text":text},ensure_ascii=False,indent=2),encoding="utf-8")
        surah_name = get_surah_name(surah)
        audio_file = download_audio(surah,ayah,str(SELECTED_AUDIO_FILE.parent/f"audio_{surah}_{ayah}.mp3"))
        SELECTED_AUDIO_FILE.write_text(audio_file,encoding="utf-8")
        audio_length = float(MP3(audio_file).info.length)
        wrapped = wrap_text(text)
        if " ".join(wrapped).split() != " ".join(text.split()).split():
            raise ValueError("الآية المعروضة لا تطابق النص الأصلي؛ تم إيقاف التصدير لتجنب حذف الكلمات.")
        block = make_block(wrapped,style)
        max_width,max_height = config.frame_width-1.0,config.frame_height-6.0
        block.scale(min(1.0,max_width/block.width,max_height/block.height)).move_to(ORIGIN+DOWN*.1)
        heading = VGroup(
            Text(surah_name,font=FONT_NAME,font_size=46,color=style["text"]),
            Text(f"آية {to_arabic_indic_digits(ayah)}",font=FONT_NAME,font_size=30,color=style["accent"]),
        ).arrange(DOWN,buff=.18).move_to(UP*(config.frame_height/2-2.1))
        divider = Line(LEFT*.55,RIGHT*.55,color=style["gold"],stroke_width=1.8).next_to(heading,DOWN,buff=.48)
        footer = Text(BRAND_NAME,font=FONT_NAME,font_size=30,color=style["info"]).move_to(DOWN*(config.frame_height/2-1.45))
        glow = VGroup(*[Circle(radius=1.5+i*.7,stroke_width=0,fill_color=style["glow"],fill_opacity=.010) for i in range(5)]).move_to(block.get_center())
        self.add(glow)
        entrance = min(.8,max(.2,audio_length*.15))
        self.play(FadeIn(heading,shift=DOWN*.12),FadeIn(divider),FadeIn(block,shift=UP*.12),FadeIn(footer),run_time=entrance,rate_func=smooth)
        self.wait(max(.1,audio_length-entrance)+.1)
        motif.clear_updaters()
