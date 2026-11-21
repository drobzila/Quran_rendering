"""Modular Quran video rendering package."""
from .config import STYLE_PRESETS
from .render import render_one, render_two_variants

__all__ = ["STYLE_PRESETS", "render_one", "render_two_variants"]
