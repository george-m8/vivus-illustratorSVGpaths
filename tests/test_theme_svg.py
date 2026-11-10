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
    assert out.split("<style>")[0] == PLAY.split("<style>")[0].replace(' id="Layer_2"', "")


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


def test_root_svg_id_is_removed():
    # Illustrator ids (Layer_N) repeat across files; nothing references them
    out = theme_svg.convert_svg(PLAY)
    assert 'id="Layer_2"' not in out
    assert out.startswith('<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" viewBox=')


# --- Inkscape files (svgs/yam): colours in style="" attributes -------------

# Trimmed from svgs/yam/yam-numeric1.svg: an outline path and a filled glyph
YAM = (
    '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<!-- Created with Inkscape -->\n'
    '<svg width="72.8mm" height="66.2mm" viewBox="0 0 72.8 66.2" version="1.1" id="svg1" xml:space="preserve" '
    'inkscape:version="1.4.2" sodipodi:docname="drawing.svg" '
    'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
    'xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" '
    'xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">'
    '<sodipodi:namedview id="namedview1" pagecolor="#ffffff"><inkscape:page x="0" y="0" id="page2" /></sodipodi:namedview>'
    '<defs id="defs1" /><g inkscape:label="Layer 1" inkscape:groupmode="layer" id="layer1" transform="translate(-120,-4)">'
    '<path style="display:inline;fill:none;stroke:#000000;stroke-width:2.8" d="m 1,1 2,2" id="path3-4" sodipodi:nodetypes="cc" />'
    '<path style="font-weight:bold;stroke-width:2.9;stroke-linecap:square;stroke-linejoin:bevel" d="m 5,5 1,1" id="text1" aria-label="1" />'
    '<path style="display:inline;fill:#000000" d="m 7,7 1,1" id="path5" />'
    '</g></svg>'
)


def styles(svg_text):
    import re
    return re.findall(r'style="([^"]*)"', svg_text)


def test_inkscape_outline_stroke_becomes_accent():
    outline = styles(theme_svg.convert_svg(YAM))[0]
    assert "stroke:var(--svg-accent,#000000)" in outline
    assert "fill:none" in outline


def test_inkscape_filled_shapes_get_accent_fill_and_no_stroke():
    # Fills show from the start; only shapes that already had a stroke are drawn
    glyph, logo = styles(theme_svg.convert_svg(YAM))[1:]
    assert glyph == "font-weight:bold;stroke-width:2.9;stroke-linecap:square;stroke-linejoin:bevel;fill:var(--svg-accent,#000000)"
    assert logo == "display:inline;fill:var(--svg-accent,#000000)"


def test_inkscape_editor_data_is_removed():
    out = theme_svg.convert_svg(YAM)
    for junk in ("inkscape", "sodipodi", "<!--", ' id="', "mm\"", "<defs", "aria-label", "xmlns:svg"):
        assert junk not in out
    assert '<svg viewBox="0 0 72.8 66.2" xmlns="http://www.w3.org/2000/svg">' in out
    assert 'd="m 1,1 2,2"' in out and 'transform="translate(-120,-4)"' in out


def test_inkscape_conversion_is_idempotent():
    once = theme_svg.convert_svg(YAM)
    assert theme_svg.convert_svg(once) == once


def test_inkscape_dasharray_is_left_to_vivus():
    yam = YAM.replace("stroke-width:2.8", "stroke-width:2.8;stroke-dasharray:none")
    assert "stroke-dasharray" not in theme_svg.convert_svg(yam)
