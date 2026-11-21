from __future__ import annotations
import random
from pathlib import Path
from .audio import download_audio, get_duration
from .config import MIN_AYAH_CHARACTERS, MIN_DURATION, MAX_DURATION, TEMP_AUDIO, TITLE_FILE, FALLBACK_TITLES, logger
from .data import QURAN_DATA, load_used
def choose_random_ayah() -> tuple[int, int, str, float]:
    """Choose and validate an unused ayah. It is reserved only after a successful export."""
    used = load_used(); candidates = []
    for s_idx, surah in enumerate(QURAN_DATA["data"]["surahs"], start=1):
        for a_idx, ayah in enumerate(surah["ayahs"], start=1):
            text = " ".join(ayah["text"].split())
            if f"{s_idx}:{a_idx}" not in used and len(text) >= MIN_AYAH_CHARACTERS:
                candidates.append((s_idx, a_idx, ayah["text"]))
    random.shuffle(candidates)
    for surah, ayah, text in candidates:
        try:
            download_audio(surah, ayah, TEMP_AUDIO); duration = get_duration(TEMP_AUDIO)
            if not MIN_DURATION <= duration <= MAX_DURATION: continue
            title = text.strip().replace("\\n", " ").replace("\\r", " ")
            if not title or len(title) > 90: title = random.choice(FALLBACK_TITLES)
            TITLE_FILE.write_text(title.strip(), encoding="utf-8")
            return surah, ayah, text, duration
        except Exception as exc:
            logger.warning("تعذر التحقق من الآية %s:%s: %s", surah, ayah, exc)
        finally:
            Path(TEMP_AUDIO).unlink(missing_ok=True)
    raise RuntimeError("لم يتم العثور على آية مناسبة غير مستخدمة")
