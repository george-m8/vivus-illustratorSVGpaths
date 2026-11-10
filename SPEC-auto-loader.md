# Spec: auto-loader (issue #1)

## Objective

The You Alright Mate Webflow site reuses icons in shared components across many pages. Right now that breaks in two ways:

- A page without the per-page body script shows a blank placeholder.
- Two placeholders with the same `id` only fill the first one.

**Goal:** one head include that works on every page. The site author drops in a placeholder like this and it just works:

```html
<div data-svg="play"></div>
```

It works any number of times per page, inside components, and when content is added later. The existing rotation feature keeps working. Sites using the current `id` + `initGlobalStaggerObserver` method keep working with no changes.

**User:** the site author, editing in Webflow, who doesn't want to touch per-page code.

## Findings from the staging site

Checked on 2026-11-10 by crawling the 9 pages of `different-hats-staging.webflow.io`:

- `vivusObserver.js` is already in the head of every page, so a head-only solution needs no Webflow changes beyond the placeholders.
- **Blank icons:** placeholders with no matching config on that page. On `/programmes/all` that's `contactShapeContainer` and `differentHatsShapeContainer`, and on `/programmes/corporate-programmes` it's `numeric4ShapeContainer` and `interviewerShapeContainer`. On `/` the config targets `pillarsShapeContainer` but the element is `pillarsRotateContainer`.
- **Copy-pasted configs:** most pages list 2-9 containers that aren't on the page. With `debug=true` each one logs an error.
- **Split timelines:** `/` calls `initGlobalStaggerObserver` twice, so two independent stagger timelines run.
- `pillarsRotateContainer` on `/` belongs to a separate site script that swaps in a rotated image on hover or click. It isn't part of this library. `initRotationControls` isn't called on any staging page. `numeric4.svg` returns 404 (issue #2).

The attribute approach fixes the first three, because each placeholder carries its own config. (An earlier note that some SVGs were missing from the repo turned out to be a local checkout that was 4 commits behind. That's fixed now.)

## Attribute API

| Attribute | Required | Default | Meaning |
|---|---|---|---|
| `data-svg` | yes | - | An SVG name (`play` → `<base>/svgs/play.svg`), or any value containing `/` or ending `.svg`, used as a URL as-is |
| `data-svg-duration` | no | `36` | Vivus `duration` |
| `data-svg-type` | no | `scenario-sync` | Vivus `type` |

- `<base>` is worked out from the `src` of the `vivusObserver.js` script tag (`document.currentScript`). On the live site that's `https://vivus-svgs.netlify.app`, and locally it's the local server, so test pages work without editing.
- The loader sets `data-svg-state` on each placeholder (`loading` → `ready` → `animated`, or `error`). This guards against processing the same element twice and also works as a styling and debugging hook.
- Theming attributes (`data-svg-accent`, etc.) are defined in [SPEC-theming.md](SPEC-theming.md).

## Behaviour

1. When the DOM is ready, find every `[data-svg]` that has no `data-svg-state` yet.
2. Fetch each distinct URL **once**. Cache the promise of its text so duplicates share one request.
3. For each placeholder, put the SVG inline and **remove the root `<svg id>`** so the page doesn't end up with duplicate IDs. Then run Pathformer and create a separate `Vivus` instance with `start: 'manual'`.
4. Watch it with one shared `IntersectionObserver` (threshold `0.5`). Use the same stagger and decay timing as today (`STAGGER_DELAY` and `DECAY_TIMEOUT`, both 800ms). Keep track of instances per element (a `WeakMap`), not per id.
5. A `MutationObserver` on `document.body` runs step 1 again on newly added subtrees, so tabs, sliders and CMS "load more" work.
6. A failed fetch or bad SVG sets `data-svg-state="error"` and logs one `console.error`. It never throws and never stops other placeholders loading.
7. Debug logging is off by default. Turn it on with `window.VIVUS_DEBUG = true` set before the script runs.

## Rotation (preserve, don't extend)

`initRotationControls` (added in `84851d6`) isn't known to be used on any site. It's kept working in case another site uses it. This spec adds no new rotation features.

- **Must keep working:** `initRotationControls(shapeConfigs, controlSelector, duration, debug)`, with the same signature, the same `id="90deg"` + `data-rotate-target` controls and the same return API (`rotateSVG`, `getRotationState`, `normalizeAngle`). The auto-loader doesn't use the `data-rotate-*` attribute namespace, so the two never clash.
- **Works with auto-loaded icons:** `rotateSVG` only looks up a container by `id` and rotates the `<svg>` inside it. So a placeholder like `<div id="x" data-svg="play">` can still be rotated by passing `[{ containerId: 'x' }]` to `initRotationControls`. The auto-loader must not strip the *placeholder's* `id`. It only removes the `id` from the injected `<svg>`. Rotation styles go on that `<svg>` element, and nothing in the auto-loader writes `transform` to it.
- **Bug fix:** the current code stores the *normalised* angle but applies the *un-normalised* one, so some sequences spin the long way. For example, 0° → 350° → 10° animates from -10° to 370°, a full 380° turn. Store the angle that was actually applied as the running value. Clicks then still take the shortest path, and `getRotationState().currentAngle` still reports a 0-360 value.

**Legacy path:** `initGlobalStaggerObserver(shapeConfigs, threshold, debug)` and `initRotationControls(...)` keep their signatures and behaviour (apart from the rotation bug fix). Elements it targets have no `data-svg`, so the two paths never touch the same element.

## Tech Stack

- Plain browser JS (ES2017+), no build step and no bundler.
- Vivus 0.4.4 and Pathformer from the jsDelivr CDN (unchanged).
- Hosted as static files on Netlify. `_headers` already allows CORS on `/js/*` and `/svgs/*`.

## Commands

```bash
uv run python -m http.server 8000
```

Then open `http://localhost:8000/test-auto.html`.

## Project Structure

```
js/vivusObserver.js   → legacy functions + new auto-loader and rotation (same file)
svgs/                 → SVG assets
test-auto.html        → new manual test page for this spec
index.html, rotation-example.html, rotation-demo.html → existing legacy demos (must keep working)
readme.md, embed.md, ROTATION.md → updated with the attribute method
```

## Code Style

Match the existing file: `const`/`let`, JSDoc block above each function, 2-space indent, `[functionName]` prefixes on debug logs.

```js
/**
 * resolveSvgUrl
 * Turns a data-svg value into a fetchable URL.
 */
function resolveSvgUrl(value) {
  if (value.includes('/') || value.endsWith('.svg')) return value;
  return `${VIVUS_BASE_URL}/svgs/${value}.svg`;
}
```

## Testing Strategy

There's no JS test framework in the repo, and adding one isn't in scope. Verify by hand in the built-in browser using `test-auto.html`, which covers:

- the same icon three times on one page
- an icon inside a repeated "component" block
- a placeholder added by a button click after load
- a bad name (`data-svg="nope"`)
- a legacy `initGlobalStaggerObserver` block on the same page
- legacy `initRotationControls` rotating an auto-loaded placeholder (by its `id`), and the 0° → 350° → 10° sequence

Also check that `index.html`, `rotation-example.html` and `rotation-demo.html` behave as before (apart from the rotation fix), and that the Network panel shows one request per distinct SVG.

## Boundaries

- **Always:** keep `initGlobalStaggerObserver` backwards compatible. Update `readme.md` and `embed.md` in the same change.
- **Ask first:** changing Vivus/Pathformer versions, renaming or moving `js/vivusObserver.js`, adding any npm or test tooling.
- **Never:** break existing live embed URLs, or require a per-page script for the new method.

## Success Criteria

- [ ] With only the head include, `<div data-svg="play">` renders and animates on any page.
- [ ] Three `data-svg="play"` on one page all render and each animates on its own as it scrolls into view, from a single network request.
- [ ] A placeholder added to the DOM after load renders and animates.
- [ ] A bad name sets `data-svg-state="error"` and the other icons still load.
- [ ] The injected markup has no duplicate `id` attributes.
- [ ] `index.html` and the `embed.md` legacy snippet behave exactly as before.
- [ ] `rotation-example.html` and `rotation-demo.html` work as before. Legacy `initRotationControls` keeps its signature and return API.
- [ ] `initRotationControls` can rotate an auto-loaded placeholder that has an `id`.
- [ ] 0° → 350° → 10° turns -10° then +20°.
- [ ] The readme and embed docs show the new method first, with the legacy method kept.

## Open Questions

- Should the new attributes take a per-element threshold, or is the global `0.5` enough?
