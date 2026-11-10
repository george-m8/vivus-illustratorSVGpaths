# Spec: theming (issue #3)

Depends on: [auto-loader](SPEC-auto-loader.md)

## Objective

Colours are currently hard-coded in each SVG, which is why `-black` and `-white` copies exist. **Goal:** set colours per instance without making new files:

```html
<div data-svg="play" data-svg-accent="#ff6b6b" data-svg-base="dark"></div>
```

Or set them from Webflow CSS on any ancestor:

```css
.hero { --svg-accent: #ff6b6b; }
```

Colourable copies of the SVGs are generated into `svgs/v2/` with the same filenames. They use CSS variables, and each variable falls back to that file's current colour, so with nothing set a v2 icon looks the same as its original. The originals in `svgs/` aren't touched, so legacy embeds don't change at all.

Once this ships, bare names in `data-svg` (e.g. `play`) resolve to `svgs/v2/play.svg` instead of `svgs/play.svg`. Nothing visibly changes for anyone already using names, because the defaults match. A full path such as `svgs/play.svg` still loads the original.

## Terms

- **Accent:** the solid, coloured strokes (currently `#fcee21`, `#000` or `#fff`).
- **Base:** the faint guide strokes, currently `#fff` at `opacity: .4`. Named "base" because the issue's word, "background", already means something else in CSS.

## CSS variable contract

| Variable | Applies to | Fallback |
|---|---|---|
| `--svg-accent` | all accent strokes | the file's original accent colour |
| `--svg-accent-1`, `-2`, `-3` | multi-colour files (`dh-logo.svg`), in stylesheet order | `--svg-accent`, then the original colour |
| `--svg-base` | base strokes (opacity stays `.4`) | `#fff` |

Example of a converted rule in `svgs/v2/play.svg`:

```css
.play-cls-1{stroke:var(--svg-accent,#fcee21);}
.play-cls-2,.play-cls-3{opacity:.4;stroke:var(--svg-base,#fff);}
```

Custom properties inherit through inline SVG, so each instance can have its own colour even though every copy of `play.svg` shares the same class rules.

## Attribute API (added to the auto-loader)

| Attribute | Sets | Values |
|---|---|---|
| `data-svg-accent` | `--svg-accent` | any CSS colour |
| `data-svg-accent-1..3` | `--svg-accent-N` | any CSS colour |
| `data-svg-base` | `--svg-base` | `light` (`#fff`), `dark` (`#000`), or any CSS colour |

The loader sets these as inline custom properties on the placeholder. Legacy-path users can get the same result with CSS on the container.

## Processing script

A new `theme_svg.py`, run with `uv run`, reads a source file or directory (the same interface as `process_svg.py`). It writes the converted files to an output directory (default `svgs/v2/`) and never modifies its input. For each `<style>` block:

1. A `stroke` declaration in a rule that also has `opacity` → `var(--svg-base, <orig>)`.
2. Any other `stroke` colour → `var(--svg-accent, <orig>)`. If a file has more than one distinct accent colour, use `var(--svg-accent-N, var(--svg-accent, <orig>))` numbered in stylesheet order.
3. It's deterministic: running it again gives byte-identical output, and inputs that already contain `var(--svg-` are copied unchanged.
4. Colour variants (filenames ending `-black`, `-white` or `-yellow`) are skipped, because colour attributes replace them in v2. Other suffixes such as `-right` and `-alt` are different shapes, so they're kept.

The script then runs once over `svgs/` (only the top-level `*.svg` files, never `v2/`), and the generated `svgs/v2/` files are committed. When a new icon is added later, it goes into `svgs/` and the script is run again.

## Project Structure

```
theme_svg.py            → new processing script
tests/test_theme_svg.py → pytest unit tests for the script
pyproject.toml          → created with `uv init --bare`, pytest as a dev dependency
svgs/*.svg              → originals, untouched
svgs/v2/*.svg           → generated colourable copies, committed
js/vivusObserver.js     → theming attributes, and name resolution switched to svgs/v2/
test-auto.html          → colour cases added
```

## Commands

```bash
uv add --dev pytest
```

```bash
uv run pytest
```

```bash
uv run python theme_svg.py ./svgs ./svgs/v2
```

```bash
uv run python -m http.server 8000
```

## Code Style

Python follows `process_svg.py`: plain functions, `main()` with `sys.argv`, and a progress line printed for each file. JS follows the auto-loader spec.

## Testing Strategy

- **pytest** (`tests/test_theme_svg.py`) with fixture strings taken from real files: the single-accent yellow file (`play`), `fiftyk` (no base), `dh-logo` (three accents), already-converted input (copied unchanged), and colour-variant filenames (skipped).
- **Visual regression by hand:** a comparison page shows each `svgs/X.svg` next to `svgs/v2/X.svg` with no attributes set. Each pair should look identical.
- **Manual:** the colour cases in `test-auto.html` (accent, base light/dark, multi-accent, CSS inheritance from an ancestor).

## Boundaries

- **Always:** keep the original colour as each variable's fallback. Run pytest before committing the generated SVGs.
- **Ask first:** changing stroke widths or geometry.
- **Never:** modify or delete files in `svgs/` (live embeds point there), or change path data or element order, since that's the animation order.

## Success Criteria

- [ ] Every top-level `svgs/X.svg` (except colour variants) has a `svgs/v2/X.svg` that uses `--svg-*` variables for stroke colours and, with no variables set, looks the same as the original.
- [ ] `git diff svgs/*.svg` is empty: the originals are unchanged.
- [ ] `data-svg="play"` loads `svgs/v2/play.svg`, and `data-svg="svgs/play.svg"` loads the original.
- [ ] `data-svg-accent="#f0f"` recolours only that instance. A second copy of the same icon nearby keeps its default.
- [ ] `data-svg-base="dark"` switches base strokes to `#000` at `.4` opacity.
- [ ] `dh-logo` with no attributes shows red, yellow and blue. `data-svg-accent` turns it into one colour, and `data-svg-accent-2` changes only the yellow.
- [ ] Setting `--svg-accent` on an ancestor in CSS recolours the icons inside it, on both the auto and legacy paths.
- [ ] `uv run pytest` passes, and running the script twice changes nothing the second time.
- [ ] The readme documents the variables, attributes and script.

## Open Questions

- Should `light`/`dark` also adjust opacity, or is `.4` right on both backgrounds?
