#!/usr/bin/env python3
"""Generate colourable copies of SVGs using CSS variables.

Strokes in rules that also set opacity become var(--svg-base, <orig>);
other strokes become var(--svg-accent, <orig>). Each variable falls back to
the original colour, so with nothing set an icon looks the same as before.

Inkscape files (no <style> block, colours in style="" attributes) are also
stripped of editor data, and their fill and stroke colours become accents.
Fills are left as they are, so they show from the start while Vivus draws
the strokes.

Usage: uv run python theme_svg.py <file_or_directory> [output_dir=svgs/v2]
"""
import re
import sys
from pathlib import Path

STYLE_RE = re.compile(r"<style>(.*?)</style>", re.S)
RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
STROKE_RE = re.compile(r"stroke:\s*(#[0-9a-fA-F]{3,6})")
OPACITY_RE = re.compile(r"(^|;)\s*opacity\s*:")
CLASS_PREFIX_RE = re.compile(r"([A-Za-z0-9_-]+?)-cls-")
ROOT_ID_RE = re.compile(r'(<svg\b[^>]*?)\s+id="[^"]*"')


# Inkscape files
COMMENT_RE = re.compile(r"<!--.*?-->\s*", re.S)
XML_DECL_RE = re.compile(r"<\?xml[^>]*\?>\s*")
NAMEDVIEW_RE = re.compile(r"<sodipodi:namedview\b[^>]*?(?:/>|>.*?</sodipodi:namedview>)", re.S)
EMPTY_DEFS_RE = re.compile(r"<defs\b[^>]*/>")
EDITOR_ATTR_RE = re.compile(r'\s+(?:inkscape:[\w-]+|sodipodi:[\w-]+|xmlns:\w+|xml:space|version|id|aria-label)="[^"]*"')
ROOT_SIZE_RE = re.compile(r'(<svg\b[^>]*?)\s+(?:width|height)="[^"]*"')
INLINE_STYLE_RE = re.compile(r'style="([^"]*)"')

# Colour copies (contact-black.svg etc.) are replaced by colour attributes in v2
COLOUR_VARIANT_RE = re.compile(r"-(black|white|yellow)$")


def accent_colours(css):
    """Distinct accent colours (lower-cased) in stylesheet order."""
    colours = []
    for _, body in RULE_RE.findall(css):
        if OPACITY_RE.search(body):
            continue
        for colour in STROKE_RE.findall(body):
            if colour.lower() not in colours:
                colours.append(colour.lower())
    return colours


def accent_var(colour, accents):
    """CSS value for an accent colour; numbered when a file has several."""
    if len(accents) > 1:  # multi-colour icons like dh-logo
        n = accents.index(colour.lower()) + 1
        return f"var(--svg-accent-{n},var(--svg-accent,{colour}))"
    return f"var(--svg-accent,{colour})"


def convert_css(css):
    """Swap stroke colours in a stylesheet for CSS variables."""
    accents = accent_colours(css)

    def convert_rule(match):
        selector, body = match.groups()
        is_base = bool(OPACITY_RE.search(body))

        def convert_stroke(stroke):
            colour = stroke.group(1)
            if is_base:
                return f"stroke:var(--svg-base,{colour})"
            return f"stroke:{accent_var(colour, accents)}"

        return selector + "{" + STROKE_RE.sub(convert_stroke, body) + "}"

    return RULE_RE.sub(convert_rule, css)


def parse_style(style):
    """style="" text -> dict of declarations, in order."""
    pairs = (d.split(":", 1) for d in style.split(";") if ":" in d)
    return {k.strip(): v.strip() for k, v in pairs}


def shape_colours(decls):
    """{property: colour} for a shape's fill and stroke. SVG fills black by default."""
    colours = {"fill": decls.get("fill", "#000000"), "stroke": decls.get("stroke", "none")}
    return {prop: c for prop, c in colours.items() if c != "none"}


def convert_inline(svg_text):
    """Theme an Inkscape SVG whose colours are in style="" attributes."""
    for pattern in (XML_DECL_RE, COMMENT_RE, NAMEDVIEW_RE, EMPTY_DEFS_RE, EDITOR_ATTR_RE):
        svg_text = pattern.sub("", svg_text)
    while ROOT_SIZE_RE.search(svg_text):  # sized by its container, like the other icons
        svg_text = ROOT_SIZE_RE.sub(r"\1", svg_text, count=1)

    shapes = [parse_style(s) for s in INLINE_STYLE_RE.findall(svg_text)]
    accents = []
    for colour in (c for decls in shapes for c in shape_colours(decls).values()):
        if colour.lower() not in accents:
            accents.append(colour.lower())

    def convert_style(match):
        decls = parse_style(match.group(1))
        decls.pop("stroke-dasharray", None)  # Vivus animates the dash itself
        for prop, colour in shape_colours(decls).items():
            decls[prop] = accent_var(colour, accents)
        return 'style="' + ";".join(f"{k}:{v}" for k, v in decls.items()) + '"'

    return '<?xml version="1.0" encoding="UTF-8"?>' + INLINE_STYLE_RE.sub(convert_style, svg_text)


def convert_svg(svg_text):
    """Return svg_text with its <style> block converted.

    Class prefixes become "<name>-v2-cls-": inline <style> rules apply to the
    whole page, so an original copy of the same icon would otherwise override
    the v2 copy's variables.
    """
    if "var(--svg-" in svg_text:
        return svg_text  # already converted
    if "<style>" not in svg_text:
        return convert_inline(svg_text)
    svg_text = CLASS_PREFIX_RE.sub(r"\1-v2-cls-", svg_text)
    svg_text = ROOT_ID_RE.sub(r"\1", svg_text, count=1)  # Layer_N ids repeat across files
    return STYLE_RE.sub(lambda m: f"<style>{convert_css(m.group(1))}</style>", svg_text)


def process(src, out):
    """Convert src (a file or directory of .svg files) into the out directory."""
    src, out = Path(src), Path(out)
    files = sorted(src.glob("*.svg")) if src.is_dir() else [src]
    out.mkdir(parents=True, exist_ok=True)
    for path in files:
        if COLOUR_VARIANT_RE.search(path.stem):
            print(f"Skipped colour variant {path}")
            continue
        (out / path.name).write_text(convert_svg(path.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"Converted {path} -> {out / path.name}")


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python theme_svg.py <file_or_directory> [output_dir=svgs/v2]")
        sys.exit(1)
    process(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "svgs/v2")


if __name__ == "__main__":
    main()
