#!/usr/bin/env python3
"""Generate colourable copies of SVGs using CSS variables.

Strokes in rules that also set opacity become var(--svg-base, <orig>);
other strokes become var(--svg-accent, <orig>). Each variable falls back to
the original colour, so with nothing set an icon looks the same as before.

Usage: uv run python theme_svg.py <file_or_directory> [output_dir=svgs/v2]
"""
import re
import sys
from pathlib import Path

STYLE_RE = re.compile(r"<style>(.*?)</style>", re.S)
RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
STROKE_RE = re.compile(r"stroke:\s*(#[0-9a-fA-F]{3,6})")
OPACITY_RE = re.compile(r"(^|;)\s*opacity\s*:")


def convert_css(css):
    """Swap stroke colours in a stylesheet for CSS variables."""
    def convert_rule(match):
        selector, body = match.groups()
        is_base = bool(OPACITY_RE.search(body))

        def convert_stroke(stroke):
            colour = stroke.group(1)
            var = "--svg-base" if is_base else "--svg-accent"
            return f"stroke:var({var},{colour})"

        return selector + "{" + STROKE_RE.sub(convert_stroke, body) + "}"

    return RULE_RE.sub(convert_rule, css)


def convert_svg(svg_text):
    """Return svg_text with its <style> block converted."""
    return STYLE_RE.sub(lambda m: f"<style>{convert_css(m.group(1))}</style>", svg_text)


def process(src, out):
    """Convert src (a file or directory of .svg files) into the out directory."""
    src, out = Path(src), Path(out)
    files = sorted(src.glob("*.svg")) if src.is_dir() else [src]
    out.mkdir(parents=True, exist_ok=True)
    for path in files:
        (out / path.name).write_text(convert_svg(path.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"Converted {path} -> {out / path.name}")


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python theme_svg.py <file_or_directory> [output_dir=svgs/v2]")
        sys.exit(1)
    process(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "svgs/v2")


if __name__ == "__main__":
    main()
