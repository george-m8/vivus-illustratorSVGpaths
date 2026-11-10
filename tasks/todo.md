# Tasks: Auto-loader and theming

Plan: [plan.md](plan.md). Specs: [auto-loader](../SPEC-auto-loader.md), [theming](../SPEC-theming.md).

Local server for every manual check:

```bash
uv run python -m http.server 8000
```

---

## Phase 0: Setup

## Task 0: Create branch and commit specs

**Description:** Branch off `main` and commit the specs and this plan, so implementation commits sit on top of an agreed baseline. Push the branch and open a **draft PR** against `main`. Netlify only builds deploy previews for PRs, and the preview URL is used to test on staging at checkpoints B and D.

**Acceptance criteria:**
- [x] On branch `feature/auto-loader-theming`
- [ ] Draft PR open against `main`, and the Netlify deploy preview builds
- [x] `SPEC*.md` and `tasks/` are committed. `demo.html` and `generate_vivus_html.py` are left alone (unrelated, ask separately).

**Verification:**
- [x] `git status` shows nothing to commit apart from the unrelated untracked files

**Dependencies:** None
**Files likely touched:** `SPEC.md`, `SPEC-auto-loader.md`, `SPEC-theming.md`, `tasks/*`
**Estimated scope:** XS

---

## Phase 1: auto-loader

## Task 1: Fix rotation long-spin bug

**Description:** In `initRotationControls`, `rotateSVG` applies `currentAngle + delta` but stores the normalised target, so the next rotation can start from the wrong place and spin the long way. Store the applied (un-normalised) angle as the running transform value, and keep `getRotationState().currentAngle` reporting 0-360.

**Acceptance criteria:**
- [ ] 0° → 350° → 10° applies `rotate(-10deg)` then `rotate(10deg)` (a +20° turn)
- [ ] 10° → 270° → 10° still takes the short path both ways
- [ ] Signature and returned API are unchanged. `getRotationState(id).currentAngle` is within 0-360.

**Verification:**
- [ ] Manual: `test-rotation.html`, clicking the sequences above and watching the transform in DevTools
- [ ] Manual: `rotation-example.html` and `rotation-demo.html` still work

**Dependencies:** None
**Files likely touched:** `js/vivusObserver.js`
**Estimated scope:** XS

## Task 2: Single placeholder renders and animates

**Description:** Add the auto-loader path: on DOM ready, find `[data-svg]` elements without `data-svg-state`, resolve the URL (name → `<base>/svgs/<name>.svg`, or used as-is if it contains `/` or ends in `.svg`), fetch, inject, remove the root `<svg>`'s `id`, run Pathformer and Vivus (`start: 'manual'`, duration/type from attributes), and animate on intersection using a module-level stagger timeline. Set `data-svg-state` through `loading` → `ready` → `animated`, or `error`. Debug logging is controlled by `window.VIVUS_DEBUG`. Create `test-auto.html` with a single icon, a full-path icon and a bad-name case.

**Acceptance criteria:**
- [ ] `<div data-svg="play">` with only the head scripts renders and animates on scroll into view
- [ ] `data-svg-duration` and `data-svg-type` are respected, with defaults of `36` and `scenario-sync`
- [ ] A bad name sets `data-svg-state="error"` with one `console.error`, and other icons still load

**Verification:**
- [ ] Manual: `http://localhost:8000/test-auto.html`, checking the state attributes in the Elements panel
- [ ] Manual: `index.html` behaves as before

**Dependencies:** None
**Files likely touched:** `js/vivusObserver.js`, `test-auto.html`
**Estimated scope:** S

## Task 3: Duplicates share one fetch and animate independently

**Description:** Cache the fetch promise for each URL, and keep Vivus instances in a `WeakMap` keyed by element. Add test cases for three copies of one icon and an icon inside a repeated "component" block.

**Acceptance criteria:**
- [ ] Three `data-svg="play"` on one page all render, from **one** network request
- [ ] Each copy animates when *it* scrolls into view, not when the first one does
- [ ] No duplicate `id` attributes in the injected markup (`document.querySelectorAll('[id]')` check)

**Verification:**
- [ ] Manual: Network panel filtered to `.svg`, then scroll the duplicates section slowly

**Dependencies:** T2
**Files likely touched:** `js/vivusObserver.js`, `test-auto.html`
**Estimated scope:** S

## Task 4: Placeholders added after load are picked up

**Description:** Add a `MutationObserver` on `document.body` that scans added subtrees for unprocessed `[data-svg]`. Add a test button that inserts a new placeholder (including a duplicate of an already-loaded icon).

**Acceptance criteria:**
- [ ] A placeholder added after load renders and animates
- [ ] A duplicate added later reuses the cached fetch (no new request)
- [ ] Re-adding an already processed element doesn't process it twice

**Verification:**
- [ ] Manual: click the insert button in `test-auto.html` and check the Network panel

**Dependencies:** T2, T3
**Files likely touched:** `js/vivusObserver.js`, `test-auto.html`
**Estimated scope:** S

## Checkpoint A: core loader
- [ ] All T2-T4 cases pass in `test-auto.html`
- [ ] `index.html` behaves as before
- [ ] No console errors other than the deliberate bad-name case

## Task 5: Legacy and rotation coexist with auto-loaded icons

**Description:** Add test sections to `test-auto.html`: a legacy `initGlobalStaggerObserver` block on the same page as auto icons, and `initRotationControls([{ containerId: 'autoRot' }])` rotating an auto-loaded `<div id="autoRot" data-svg="play">`. Fix anything that doesn't work.

**Acceptance criteria:**
- [ ] The legacy block and auto icons both render and animate on the same page
- [ ] Rotation buttons rotate the auto-loaded icon, including the 0° → 350° → 10° sequence
- [ ] The placeholder keeps its `id`, and only the injected `<svg>` loses its own

**Verification:**
- [ ] Manual: `test-auto.html` legacy and rotation sections
- [ ] Manual: `rotation-example.html`, `rotation-demo.html`, `test-rotation.html` and `index.html` all behave as before

**Dependencies:** T1, T2
**Files likely touched:** `test-auto.html`, possibly `js/vivusObserver.js`
**Estimated scope:** S

## Task 6: Document the attribute method

**Description:** Lead `readme.md` and `embed.md` with the attribute method (head include + placeholders only), and keep the legacy method under its own heading. Add a short note to `ROTATION.md` on rotating auto-loaded icons and the bug fix. Fix the `python3` command in the readme to `uv run python`.

**Acceptance criteria:**
- [ ] The readme and embed docs show a copy-pasteable head include + placeholder example with every attribute listed
- [ ] The legacy docs are still present and accurate
- [ ] `ROTATION.md` mentions auto-loaded icons

**Verification:**
- [ ] Manual: follow `embed.md` from scratch on a blank local page and get an animated icon
- [ ] Manual (staging): on `different-hats-staging.webflow.io`, load `vivusObserver.js` from `https://deploy-preview-<PR#>--vivus-svgs.netlify.app` plus a `data-svg` placeholder (from the console) and confirm it renders next to the existing legacy icons

**Dependencies:** T2-T5
**Files likely touched:** `readme.md`, `embed.md`, `ROTATION.md`
**Estimated scope:** S

## Checkpoint B: auto-loader shippable
- [ ] All auto-loader success criteria in the spec are ticked
- [ ] Human review. Decide whether to merge phase 1 now (deploys live) or wait for theming.

---

## Phase 2: theming

## Task 7: theme_svg.py converts a standard SVG

**Description:** Set up `uv init --bare` and `uv add --dev pytest`, and add `.venv/` and `__pycache__/` to `.gitignore`. Write `theme_svg.py <src> [out=svgs/v2]` for the standard case: a stroke in a rule with `opacity` becomes `var(--svg-base,<orig>)`, and other strokes become `var(--svg-accent,<orig>)`. It writes to the output directory and never modifies its input. Test with a fixture taken from `play.svg`.

**Acceptance criteria:**
- [ ] `play.svg` converts to the expected `<style>` block, with all geometry byte-identical
- [ ] The input file is unchanged after a run
- [ ] Running twice gives identical output

**Verification:**
- [ ] Tests pass: `uv run pytest`

**Dependencies:** None (can run alongside phase 1)
**Files likely touched:** `pyproject.toml`, `.gitignore`, `theme_svg.py`, `tests/test_theme_svg.py`
**Estimated scope:** S

## Task 8: theme_svg.py edge cases

**Description:** Handle multi-accent files (`dh-logo`: `--svg-accent-N` in stylesheet order, falling back to `--svg-accent`), accent-only files (`fiftyk`), already-converted input (copied unchanged), and colour variants (filenames ending `-black`, `-white` or `-yellow` are skipped; `-right`/`-alt` are kept). Directory mode processes only top-level `*.svg`.

**Acceptance criteria:**
- [ ] A pytest case passes for each of: `dh-logo`, `fiftyk`, already-converted input
- [ ] `contact-black.svg` and `dh-logo-yellow.svg` are skipped, and `numeric1-right.svg` is converted
- [ ] Directory mode never reads from `svgs/v2/`

**Verification:**
- [ ] Tests pass: `uv run pytest`

**Dependencies:** T7
**Files likely touched:** `theme_svg.py`, `tests/test_theme_svg.py`
**Estimated scope:** S

## Task 9: Generate svgs/v2/ and comparison page

**Description:** Run the script over `svgs/` and commit `svgs/v2/`. Add `test-themed.html`, which shows each original next to its v2 copy (inline-injected, no variables set) on a dark background.

**Acceptance criteria:**
- [ ] Every top-level `svgs/X.svg` except colour variants has a `svgs/v2/X.svg` (24 files)
- [ ] Every pair looks identical on the comparison page
- [ ] `git diff svgs/*.svg` is empty

**Verification:**
- [ ] Commands: `uv run python theme_svg.py ./svgs ./svgs/v2`, then `git diff --stat svgs/*.svg`
- [ ] Manual: `http://localhost:8000/test-themed.html`

**Dependencies:** T8
**Files likely touched:** `svgs/v2/*` (generated), `test-themed.html`
**Estimated scope:** S (many generated files, little authored)

## Checkpoint C: v2 assets
- [ ] `uv run pytest` passes
- [ ] The comparison page shows no differences
- [ ] Originals are unchanged

## Task 10: Loader applies colours and resolves names to v2

**Description:** The loader sets `--svg-accent`, `--svg-accent-1..3` and `--svg-base` (`light` → `#fff`, `dark` → `#000`, otherwise used as-is) as inline custom properties on the placeholder. Bare names now resolve to `svgs/v2/<name>.svg`. Add colour cases to `test-auto.html`: per-instance accent next to a default copy, base dark, `dh-logo` single accent and `accent-2` only, ancestor CSS variable on both the auto and legacy paths, and a v1 + v2 copy of the same icon on one page.

**Acceptance criteria:**
- [ ] `data-svg-accent="#f0f"` recolours only that instance
- [ ] `dh-logo` defaults to three colours, `data-svg-accent` makes it one colour, and `data-svg-accent-2` changes only the yellow
- [ ] `data-svg="play"` requests `svgs/v2/play.svg`, and `svgs/play.svg` still loads the original

**Verification:**
- [ ] Manual: colour section of `test-auto.html`, plus the Network panel for URL resolution

**Dependencies:** T2, T9
**Files likely touched:** `js/vivusObserver.js`, `test-auto.html`
**Estimated scope:** S

## Task 11: Document theming

**Description:** Add a theming section to the readme covering the variables, attributes, `light`/`dark`, the multi-accent icons and how to add a new icon (put it in `svgs/`, then run the script). Add a colour example to `embed.md`, plus a table mapping old variant files to v2 attributes (e.g. `contact-black.svg` → `data-svg="contact" data-svg-accent="#000"`, `dh-logo-yellow.svg` → `data-svg="dh-logo" data-svg-accent="#fcee21"`).

**Acceptance criteria:**
- [ ] The readme documents every variable and attribute in the theming spec
- [ ] The "add a new icon" steps use `uv run`

**Verification:**
- [ ] Manual: follow the readme to add a test icon end to end, then delete it

**Dependencies:** T10
**Files likely touched:** `readme.md`, `embed.md`
**Estimated scope:** XS

## Checkpoint D: complete
- [ ] All success criteria in both specs are ticked
- [ ] `uv run pytest` passes, and the legacy demo pages are unchanged
- [ ] Human review → merge to `main` (deploys live)
