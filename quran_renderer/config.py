from __future__ import annotations
import logging
from pathlib import Path
from manim import config

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR
ASSETS_DIR = ROOT_DIR / "assets"
FONT_DIR = ASSETS_DIR / "fonts"
QURAN_FILE = ROOT_DIR / "quran.json"
USED_FILE = ROOT_DIR / "used_ayahs.json"
FONT_FILE = ROOT_DIR / "Amiri-Regular.ttf"
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("quran_renderer")
config.frame_width, config.frame_height = 9, 16
config.pixel_width, config.pixel_height = 1080, 1920
VIDEO_TITLE = ""
FALLBACK_TITLES = ["تلاوة قرآنية مؤثرة 🌿", "راحة نفسية مع القرآن الكريم", "آيات تريح القلب 🤍", "استمع لكلام الله بخشوع", "تلاوة هادئة للقلب والروح", "القرآن الكريم بصوت جميل", "آيات من القرآن الكريم", "تلاوة قصيرة ومؤثرة", "سكينة وطمأنينة مع القرآن", "أجمل التلاوات القرآنية", "دقيقة من الجمال القرآني", "تلاوة تلامس القلب", "نور القرآن الكريم ✨", "كلام الله يريح القلوب", "استمع وتدبر آيات الله"]
FONT_NAME = "Amiri"
FONT_SIZE_AYAH = 72
WRAP_WIDTH_CHARS = 42
MAX_LINES_PER_PAGE = 5
LINE_SPACING = 0.5
BRAND_NAME = "نسمات القرآن"
RECITERS = ["ar.husary", "ar.abdulbasitmurattal", "ar.minshawi", "ar.mahermuaiqly"]
RECITER = "ar.husary"
SHORTS_OUTPUT = "Quran_Shorts.mp4"
MIN_AYAH_CHARACTERS, MIN_DURATION, MAX_DURATION = 100, 8, 25
TEMP_AUDIO = str(ROOT_DIR / "temp.mp3")
SELECTED_AYAH_FILE = ROOT_DIR / "selected_ayah.json"
SELECTED_AUDIO_FILE = ROOT_DIR / "selected_audio.txt"
TITLE_FILE = ROOT_DIR / "title.txt"

# Each preset defines a genuinely contrasting palette, text contrast, and ornament behavior.
STYLE_PRESETS = {
    "green": {"name":"زمردي","top":"#062B23","bottom":"#0B4033","text":"#FFF9E8","accent":"#58B99A","info":"#C8DAD1","gold":"#D6B66D","glow":"#56A98B","motif_opacity":0.10,"motion":0.0},
    "midnight": {"name":"ليلي","top":"#071426","bottom":"#132B49","text":"#F5F7FF","accent":"#82B9EA","info":"#C8D5E8","gold":"#E6C77A","glow":"#5A8BC2","motif_opacity":0.09,"motion":0.025},
    "royal": {"name":"ملكي","top":"#211336","bottom":"#38224F","text":"#FFF7E8","accent":"#C6A0F0","info":"#D8CBEA","gold":"#E5C77A","glow":"#A982D5","motif_opacity":0.09,"motion":0.0},
    "ocean": {"name":"فيروزي عميق","top":"#06343B","bottom":"#075360","text":"#F0FCFC","accent":"#65C6CE","info":"#C5E5E7","gold":"#D8B978","glow":"#45AAB5","motif_opacity":0.08,"motion":0.018},
    "sand": {"name":"صحراوي","top":"#F8EEDC","bottom":"#E5D1AE","text":"#38291B","accent":"#8B6334","info":"#66513B","gold":"#A87938","glow":"#C39A58","motif_opacity":0.08,"motion":0.0},
    "slate": {"name":"رصين","top":"#171D26","bottom":"#303B49","text":"#F5F5F2","accent":"#A9C0D2","info":"#D0D9E1","gold":"#C7A96B","glow":"#879BAE","motif_opacity":0.07,"motion":0.012},
    "burgundy": {"name":"عنابي","top":"#300D1D","bottom":"#541A32","text":"#FFF5ED","accent":"#D68AAB","info":"#E5C8D4","gold":"#D8B26C","glow":"#B75B83","motif_opacity":0.09,"motion":0.0},
    "ivory": {"name":"عاجي","top":"#FFF8EC","bottom":"#EDE1CA","text":"#33271D","accent":"#8E6B45","info":"#665442","gold":"#AD8247","glow":"#C5A56B","motif_opacity":0.06,"motion":0.0},
    "obsidian": {"name":"فضي أسود","top":"#090B0F","bottom":"#20242B","text":"#F7F7F7","accent":"#AEB9C6","info":"#CFD4DB","gold":"#B9C4CF","glow":"#8292A4","motif_opacity":0.055,"motion":0.01},
    "plum": {"name":"بنفسجي هادئ","top":"#241B35","bottom":"#3A2B50","text":"#F9F3FF","accent":"#BFA6DE","info":"#D9CDE9","gold":"#D8BD84","glow":"#9275BA","motif_opacity":0.075,"motion":0.015},
}
MOTIF_KEYS = ["rosette", "eight_point_star", "nested_medallion", "diamond_lattice", "flower", "archwork"]
