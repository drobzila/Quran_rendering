from quran_renderer.config import STYLE_PRESETS, MOTIF_KEYS
from quran_renderer.scene import wrap_text


def test_has_ten_styles():
    assert len(STYLE_PRESETS) == 10


def test_style_presets_have_required_fields():
    required = {"name", "top", "bottom", "text", "accent", "info", "gold", "glow", "motif_opacity", "motion"}
    for style in STYLE_PRESETS.values():
        assert required <= set(style)


def test_motif_catalog():
    assert len(MOTIF_KEYS) == 6
    assert len(set(MOTIF_KEYS)) == len(MOTIF_KEYS)


def test_wrap_text_preserves_every_word():
    sample = " ".join(["هذه"] * 80)
    lines = wrap_text(sample)
    assert " ".join(lines).split() == sample.split()
    assert all(lines)
