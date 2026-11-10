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
        ".play-v2-cls-1{stroke:var(--svg-accent,#fcee21);}"
        ".play-v2-cls-1,.play-v2-cls-2,.play-v2-cls-3{fill:none;stroke-miterlimit:10;stroke-width:6px;}"
        ".play-v2-cls-1,.play-v2-cls-3{stroke-linecap:square;}"
        ".play-v2-cls-2,.play-v2-cls-3{opacity:.4;stroke:var(--svg-base,#fff);}"
    )


def test_geometry_is_untouched_apart_from_class_names():
    out = theme_svg.convert_svg(PLAY)
    assert out.split("</style>")[1] == PLAY.split("</style>")[1].replace("play-cls-", "play-v2-cls-")
    assert out.split("<style>")[0] == PLAY.split("<style>")[0]


def test_v2_class_names_do_not_clash_with_originals():
    # Inline <style> rules are page-global: an original play.svg on the same page
    # must not override a v2 copy's variables, so v2 uses its own class names.
    out = theme_svg.convert_svg(PLAY)
    assert "play-cls-" not in out
    assert out.count("play-v2-cls-") == PLAY.count("play-cls-")


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


# --- T8: edge cases --------------------------------------------------------

DH_LOGO_STYLE = (
    ".dh-logo-cls-1{stroke:#ed1c24;}.dh-logo-cls-1,.dh-logo-cls-2,.dh-logo-cls-3{fill:none;stroke-miterlimit:10;stroke-width:6px;}"
    ".dh-logo-cls-2{stroke:#fcee21;}.dh-logo-cls-2,.dh-logo-cls-3{stroke-linecap:square;}.dh-logo-cls-3{stroke:#3fa9f5;}"
)
FIFTYK_STYLE = ".fiftyk-cls-1{fill:none;stroke:#fcee21;stroke-miterlimit:10;stroke-width:6px}"


def wrap(style):
    return f'<svg viewBox="0 0 10 10"><defs><style>{style}</style></defs><circle class="x" r="1"/></svg>'


def test_multi_accent_numbers_colours_in_stylesheet_order():
    assert style_of(theme_svg.convert_svg(wrap(DH_LOGO_STYLE))) == (
        ".dh-logo-v2-cls-1{stroke:var(--svg-accent-1,var(--svg-accent,#ed1c24));}"
        ".dh-logo-v2-cls-1,.dh-logo-v2-cls-2,.dh-logo-v2-cls-3{fill:none;stroke-miterlimit:10;stroke-width:6px;}"
        ".dh-logo-v2-cls-2{stroke:var(--svg-accent-2,var(--svg-accent,#fcee21));}"
        ".dh-logo-v2-cls-2,.dh-logo-v2-cls-3{stroke-linecap:square;}"
        ".dh-logo-v2-cls-3{stroke:var(--svg-accent-3,var(--svg-accent,#3fa9f5));}"
    )


def test_accent_only_file_has_no_base():
    assert style_of(theme_svg.convert_svg(wrap(FIFTYK_STYLE))) == (
        ".fiftyk-v2-cls-1{fill:none;stroke:var(--svg-accent,#fcee21);stroke-miterlimit:10;stroke-width:6px}"
    )


def test_repeated_accent_colour_is_single_accent():
    style = ".a{stroke:#fcee21;}.b{stroke:#FCEE21;}.c{opacity:.4;stroke:#fff;}"
    out = style_of(theme_svg.convert_svg(wrap(style)))
    assert "--svg-accent-" not in out
    assert out.count("var(--svg-accent,") == 2


def test_stroke_opacity_is_not_treated_as_base():
    out = style_of(theme_svg.convert_svg(wrap(".a{stroke-opacity:.5;stroke:#fcee21;}")))
    assert out == ".a{stroke-opacity:.5;stroke:var(--svg-accent,#fcee21);}"


def test_already_converted_input_is_unchanged():
    once = theme_svg.convert_svg(PLAY)
    assert theme_svg.convert_svg(once) == once


def test_directory_skips_colour_variants_and_subfolders(tmp_path):
    src = tmp_path / "svgs"
    out = src / "v2"
    out.mkdir(parents=True)
    for name in ["play", "numeric1-right", "book-alt", "contact-black", "dh-logo-white", "dh-logo-yellow"]:
        (src / f"{name}.svg").write_text(PLAY)
    (out / "stale.svg").write_text(PLAY)

    theme_svg.process(src, out)

    assert sorted(p.name for p in out.glob("*.svg")) == ["book-alt.svg", "numeric1-right.svg", "play.svg", "stale.svg"]
