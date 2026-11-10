"""Tests for theme_svg.py. Run with: uv run pytest"""
from pathlib import Path

import theme_svg

# Fixtures copied from real files in svgs/
PLAY = (
    '<?xml version="1.0" encoding="UTF-8"?><svg id="Layer_2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 126.95 126.95">'
    '<defs><style>.play-cls-1{stroke:#fcee21;}.play-cls-1,.play-cls-2,.play-cls-3{fill:none;stroke-miterlimit:10;stroke-width:6px;}'
    '.play-cls-1,.play-cls-3{stroke-linecap:square;}.play-cls-2,.play-cls-3{opacity:.4;stroke:#fff;}</style></defs>'
    '<circle class="play-cls-2" cx="63.48" cy="63.48" r="60.48"/><rect class="play-cls-3" x="21.74" y="21.78" width="83.48" height="83.48"/>'
    '<polygon class="play-cls-1" points="21.69 103.21 101.86 63.48 21.69 23.74 21.69 103.21"/></svg>'
)


def style_of(svg_text):
    return svg_text.split("<style>")[1].split("</style>")[0]


# --- T7: standard accent + base -------------------------------------------

def test_play_accent_and_base_become_variables():
    assert style_of(theme_svg.convert_svg(PLAY)) == (
        ".play-cls-1{stroke:var(--svg-accent,#fcee21);}"
        ".play-cls-1,.play-cls-2,.play-cls-3{fill:none;stroke-miterlimit:10;stroke-width:6px;}"
        ".play-cls-1,.play-cls-3{stroke-linecap:square;}"
        ".play-cls-2,.play-cls-3{opacity:.4;stroke:var(--svg-base,#fff);}"
    )


def test_geometry_is_untouched():
    out = theme_svg.convert_svg(PLAY)
    assert out.split("</style>")[1] == PLAY.split("</style>")[1]
    assert out.split("<style>")[0] == PLAY.split("<style>")[0]


def test_conversion_is_deterministic():
    assert theme_svg.convert_svg(PLAY) == theme_svg.convert_svg(PLAY)


def test_process_writes_output_and_leaves_input(tmp_path):
    src = tmp_path / "svgs"
    out = src / "v2"
    src.mkdir()
    (src / "play.svg").write_text(PLAY)

    theme_svg.process(src, out)
    first = (out / "play.svg").read_text()
    theme_svg.process(src, out)

    assert (src / "play.svg").read_text() == PLAY
    assert "var(--svg-accent,#fcee21)" in first
    assert (out / "play.svg").read_text() == first
