"""Steal slug+fence: NFKD slug and run-length fence close (ideas only)."""
from book2skill import split_chapters as sc_mod


def test_slug_cafe_au_lait() -> None:
    assert sc_mod.slug("Café au lait") == "cafe-au-lait"


def test_5_backtick_open_not_closed_by_3_backtick() -> None:
    text = "`````\n# Hidden one\n```\n# Hidden two\n`````\n# Visible\n"
    titles = [r["title"] for r in sc_mod.detect_chapters(text)]
    assert titles == ["Visible"]

