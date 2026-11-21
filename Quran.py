"""Backward-compatible entry point for the modular Quran renderer.

Existing workflows can continue running: python Quran.py
New code should import from quran_renderer directly.
"""
from __future__ import annotations
import os
from manim import *
from quran_renderer.config import STYLE_PRESETS, SHORTS_OUTPUT
from quran_renderer.data import QURAN_DATA, load_used, save_used, get_surah_name, to_arabic_indic_digits, mark_ayah_used
from quran_renderer.audio import download_audio, get_duration
from quran_renderer.selection import choose_random_ayah
from quran_renderer.visuals import build_background, decorative_motif, decorative_divider, ayah_number_circle, progress_bar, corner_ornament
from quran_renderer.scene import QuranScene as _QuranScene, wrap_text, paginate, make_block


class QuranScene(_QuranScene):
    """Expose the scene in this module so Manim can discover it."""
    pass
from quran_renderer.render import render_one, render_two_variants

shorts_output = SHORTS_OUTPUT

if __name__ == "__main__":
    if os.environ.get("RENDER_TWO", "1") == "1":
        render_two_variants()
    else:
        render_one(os.environ.get("OUTPUT_FILE", shorts_output))
