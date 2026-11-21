from __future__ import annotations
import logging
from pathlib import Path
from manim import config
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
ASSETS_DIR = ROOT_DIR / "assets"
FONT_DIR = ASSETS_DIR / "fonts"
QURAN_FILE = DATA_DIR / "quran.json"
USED_FILE = DATA_DIR / "used_ayahs.json"
FONT_FILE = FONT_DIR / "Amiri-Regular.ttf"
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("quran_renderer")
config.frame_width, config.frame_height = 9, 16
config.pixel_width, config.pixel_height = 1080, 1920
VIDEO_TITLE = ""
FALLBACK_TITLES = ["تلاوة قرآنية مؤثرة 🌿", "راحة نفسية مع القرآن الكريم", "آيات تريح القلب 🤍", "استمع لكلام الله بخشوع", "تلاوة هادئة للقلب والروح", "القرآن الكريم بصوت جميل", "آيات من القرآن الكريم", "تلاوة قصيرة ومؤثرة", "سكينة وطمأنينة مع القرآن", "أجمل التلاوات القرآنية", "دقيقة من الجمال القرآني", "تلاوة تلامس القلب", "نور القرآن الكريم ✨", "كلام الله يريح القلوب", "استمع وتدبر آيات الله"]
FONT_NAME = "Amiri"
BRAND_NAME = "نسمات القرآن"
RECITER = "ar.husary"
SHORTS_OUTPUT = "Quran_Shorts.mp4"
MIN_AYAH_CHARACTERS, MIN_DURATION, MAX_DURATION = 100, 8, 25
TEMP_AUDIO = str(ROOT_DIR / "temp.mp3")
SELECTED_AYAH_FILE = ROOT_DIR / "selected_ayah.json"
SELECTED_AUDIO_FILE = ROOT_DIR / "selected_audio.txt"
TITLE_FILE = ROOT_DIR / "title.txt"
STYLE_PRESETS = {
"green": {"name":"الأخضر الإسلامي","top":"#F2FFF7","bottom":"#FFFFFF","text":"#1B5E20","accent":"#2E7D32","info":"#5F6962","gold":"#B89A55","glow":"#2E7D32"},
"midnight": {"name":"الأزرق الليلي","top":"#081A33","bottom":"#142D4E","text":"#F3F7FF","accent":"#75B9F2","info":"#C5D4E8","gold":"#E6C77A","glow":"#75B9F2"},
"royal": {"name":"البنفسجي الملكي","top":"#211333","bottom":"#43265D","text":"#FFF7FF","accent":"#D6A7F0","info":"#E2D2EA","gold":"#F0CF83","glow":"#C58BE8"},
"ocean": {"name":"المحيط الفيروزي","top":"#E8FAFC","bottom":"#C9EEF1","text":"#064B59","accent":"#087E8B","info":"#426A70","gold":"#B78A43","glow":"#39A8B5"},
"sand": {"name":"الذهبي الصحراوي","top":"#FFF8E8","bottom":"#EEDDBB","text":"#513B20","accent":"#9B7135","info":"#76664F","gold":"#B18A45","glow":"#C49A50"},
"slate": {"name":"الرمادي الفاخر","top":"#202833","bottom":"#394653","text":"#F4F1E8","accent":"#B7C5D4","info":"#D1D8DF","gold":"#D6B56D","glow":"#9EADBC"},
}
MOTIF_KEYS = ["rosette", "eight_point_star", "nested_medallion", "diamond_lattice", "flower", "archwork"]
