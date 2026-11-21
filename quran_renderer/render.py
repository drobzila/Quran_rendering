from __future__ import annotations
import glob
import json
import os
import random
import subprocess
import uuid
from pathlib import Path
from mutagen.mp3 import MP3
from .audio import download_audio
from .config import ROOT_DIR, SELECTED_AYAH_FILE, SELECTED_AUDIO_FILE, STYLE_PRESETS, MOTIF_KEYS, SHORTS_OUTPUT, logger
from .data import get_surah_name, mark_ayah_used
from .scene import QuranScene
from .selection import choose_random_ayah

def _render_scene(style_key: str, motif_key: str) -> tuple[str, str, int, int]:
    selected = json.loads(SELECTED_AYAH_FILE.read_text(encoding="utf-8"))
    surah, ayah = int(selected["surah"]), int(selected["ayah"])
    token = uuid.uuid4().hex[:10]
    scene_name = f"QuranScene_{style_key}_{motif_key}_{token}"
    env = os.environ.copy(); env["QURAN_STYLE"] = style_key; env["QURAN_MOTIF"] = motif_key
    scene_file = ROOT_DIR / "Quran.py"
    subprocess.run(["manim","-qh",str(scene_file),"QuranScene","-o",scene_name],check=True,cwd=ROOT_DIR,env=env)
    matches = glob.glob(str(ROOT_DIR / "media" / "videos" / "**" / f"*{scene_name}.mp4"),recursive=True)
    if not matches: raise FileNotFoundError(f"لم يتم العثور على فيديو Manim الناتج: {scene_name}")
    video = max(matches,key=os.path.getmtime)
    audio = SELECTED_AUDIO_FILE.read_text(encoding="utf-8").strip()
    return video,audio,surah,ayah

def _mux(video: str, audio: str, output_path: str) -> None:
    output = Path(output_path); output.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(["ffmpeg","-y","-i",video,"-i",audio,"-vf","scale=1080:1920","-c:v","libx264","-c:a","copy","-shortest",str(output)],check=True,cwd=ROOT_DIR)
    if not output.exists() or output.stat().st_size == 0: raise RuntimeError("لم يتم إنشاء ملف الفيديو النهائي")

def render_one(output_path: str = SHORTS_OUTPUT) -> str:
    """Render one fresh ayah and reserve it only after the final MP4 is valid."""
    surah,ayah,text,duration = choose_random_ayah()
    SELECTED_AYAH_FILE.write_text(json.dumps({"surah":surah,"ayah":ayah,"text":text},ensure_ascii=False,indent=2),encoding="utf-8")
    style_key = os.environ.get("QURAN_STYLE","green")
    if style_key not in STYLE_PRESETS: style_key = "green"
    motif_key = os.environ.get("QURAN_MOTIF","rosette")
    video,audio,surah,ayah = _render_scene(style_key,motif_key)
    _mux(video,audio,output_path)
    mark_ayah_used(surah,ayah)
    logger.info("تم إنتاج الفيديو: %s",output_path)
    return output_path

def render_two_variants() -> list[str]:
    """Create two videos using different non-green palettes and different ornaments."""
    styles = random.sample([key for key in STYLE_PRESETS if key != "green"],2)
    motifs = random.sample(MOTIF_KEYS,2)
    outputs = []
    for index,(style_key,motif_key) in enumerate(zip(styles,motifs),start=1):
        surah,ayah,text,_ = choose_random_ayah()
        SELECTED_AYAH_FILE.write_text(json.dumps({"surah":surah,"ayah":ayah,"text":text},ensure_ascii=False,indent=2),encoding="utf-8")
        logger.info("الفيديو %d: الآية %s:%s، النمط %s، الزخرفة %s",index,surah,ayah,STYLE_PRESETS[style_key]["name"],motif_key)
        video,audio,surah,ayah = _render_scene(style_key,motif_key)
        output = str(ROOT_DIR / f"Quran_Shorts_{index}.mp4")
        _mux(video,audio,output)
        mark_ayah_used(surah,ayah)
        outputs.append(output)
        try:
            from bot import notify_exported
            notify_exported(get_surah_name(surah),surah,ayah,text,float(MP3(audio).info.length),output)
        except Exception as exc:
            logger.warning("تعذر إرسال إشعار Telegram، لكن الفيديو تم تصديره بنجاح: %s",exc)
    logger.info("اكتمل إنتاج نسختين مختلفتين بآيتين وتصميمين وزخرفتين.")
    return outputs
