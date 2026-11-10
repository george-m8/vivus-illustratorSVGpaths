# Capability Map: Webflow-friendly loading and theming

Covers GitHub issues #1 (same JS on every page) and #3 (dynamic colouring).

| Module id | Responsibility | Depends on | Spec |
|---|---|---|---|
| auto-loader | Find SVG placeholders by attribute on any page, load each one once, and animate every copy on its own. The legacy `initGlobalStaggerObserver` and `initRotationControls` keep working. | - | [SPEC-auto-loader.md](SPEC-auto-loader.md) |
| theming | SVGs coloured with CSS variables (accent + base), set per instance with attributes or CSS. | auto-loader (attribute API) | [SPEC-theming.md](SPEC-theming.md) |

Build order: auto-loader → theming

## Decisions so far

- Two specs, built in the order above.
- Auto-loading is added to the existing `js/vivusObserver.js`, so Webflow head includes pick it up without any changes.
- Colourable SVGs go in a new `svgs/v2/` folder. The originals in `svgs/` stay exactly as they are, so live embeds don't change. (This replaces an earlier decision to rewrite the files in place.)
- The loader also picks up placeholders that get added after page load.
- Attributes use the short `data-svg` prefix, and CSS variables use `--svg-*`. The faint strokes are called "base".
- `v2/` leaves out `-black`/`-white`/`-yellow` colour variants, because colour attributes replace them.
