from __future__ import annotations
import json
from .config import QURAN_FILE, USED_FILE
with QURAN_FILE.open("r", encoding="utf-8") as stream:
    QURAN_DATA = json.load(stream)
def load_used() -> set[str]:
    if not USED_FILE.exists(): return set()
    with USED_FILE.open("r", encoding="utf-8") as stream: return set(json.load(stream))
def save_used(data: set[str]) -> None:
    USED_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = USED_FILE.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(sorted(data), ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(USED_FILE)
def mark_ayah_used(surah: int, ayah: int) -> None:
    used = load_used(); used.add(f"{surah}:{ayah}"); save_used(used)
def get_surah_name(surah: int) -> str:
    return QURAN_DATA["data"]["surahs"][surah - 1]["name"]
def to_arabic_indic_digits(value: object) -> str:
    return str(value).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))
