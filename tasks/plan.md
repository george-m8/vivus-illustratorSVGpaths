# Implementation Plan: Auto-loader and theming (issues #1, #3)

## Overview

This builds the two modules in [SPEC.md](../SPEC.md), in order:

1. **auto-loader** ([spec](../SPEC-auto-loader.md)): `data-svg` placeholders that work on any page from the existing head include.
2. **theming** ([spec](../SPEC-theming.md)): colourable copies in `svgs/v2/`, controlled by `data-svg-accent` / `data-svg-base` or CSS variables.

Legacy `initGlobalStaggerObserver` and `initRotationControls` keep working throughout. Task-by-task checklist: [todo.md](todo.md).

## Dependency graph

```
T1 rotation bug fix ─────────────────────────────┐
                                                  │
T2 single placeholder renders + animates          │
 ├── T3 duplicates: one fetch, independent anims  │
 ├── T4 late-added placeholders                   │
 └── T5 legacy + rotation coexistence ◄───────────┘
      └── T6 docs (auto-loader)
           │
T7 theme_svg.py: single accent + base (pytest)
 └── T8 theme_svg.py edge cases
      └── T9 generate svgs/v2/ + comparison page
           └── T10 loader: colour attributes + v2 name resolution  (also needs T2)
                └── T11 docs (theming)
```

T1 and T7-T9 don't depend on the loader and could run in parallel with T2-T4. The plan is still written as one sequence, because everything except T7-T9 touches `js/vivusObserver.js`.

## Architecture decisions

- **One file, two code paths.** The new loader is added to `js/vivusObserver.js`. Legacy functions are untouched, apart from the rotation fix in T1. Shared pieces (stagger scheduler, SVG fetch) are pulled into internal helpers only when the second caller needs them, not before.
- **Stagger timeline.** All auto-loaded placeholders share one `IntersectionObserver` and one global stagger timeline. Each legacy `initGlobalStaggerObserver` call keeps its own timeline, as it does today.
- **Instance state lives in a `WeakMap` keyed by element**, not on config objects or IDs. That's what lets duplicates animate independently.
- **Base URL from `document.currentScript`**, captured at script evaluation time (it's `null` inside callbacks). Fallback: `https://vivus-svgs.netlify.app`.
- **v2 SVGs are generated and committed**, not built on deploy. Netlify has no build step, and this keeps it that way.
- **Testing:** pytest (via `uv`) for the only pure-logic module (`theme_svg.py`). The JS gets manual browser checks against `test-auto.html`, because adding JS test tooling is out of scope (spec boundary: ask first).

## Branching and release

- Work on `feature/auto-loader-theming`. One commit per task, pushed to the draft PR so the deploy preview stays current.
- **Pushing to `main` deploys to every live site immediately**, because Netlify serves `main`. So:
  - Don't merge until a checkpoint has passed.
  - The auto-loader (phase 1) can ship on its own before theming.

## Task list

### Phase 0: Setup
- [x] T0: Create branch, commit specs and plan (draft PR #5, preview: https://deploy-preview-5--vivus-svgs.netlify.app)

### Phase 1: auto-loader
- [x] T1: Fix rotation long-spin bug (legacy)
- [x] T2: Single `data-svg` placeholder renders and animates
- [x] T3: Duplicate placeholders share one fetch and animate independently
- [ ] T4: Placeholders added after load are picked up

### Checkpoint A: core loader
- [ ] `test-auto.html` cases from T2-T4 pass in the browser, and `index.html` is unchanged

- [ ] T5: Legacy observer and rotation coexist with auto-loaded icons
- [ ] T6: Document the attribute method (readme, embed, ROTATION)

### Checkpoint B: auto-loader shippable
- [ ] All auto-loader success criteria in the spec are met
- [ ] Tried against the staging Webflow site (see T6 verification)
- [ ] Human review → optional merge/deploy of phase 1

### Phase 2: theming
- [ ] T7: `theme_svg.py` converts a standard accent + base SVG (with pytest)
- [ ] T8: `theme_svg.py` handles multi-accent, accent-only and colour-variant cases
- [ ] T9: Generate `svgs/v2/` and a comparison page

### Checkpoint C: v2 assets
- [ ] `uv run pytest` passes, every v2 icon matches its original, and `git diff svgs/*.svg` is empty

- [ ] T10: Loader applies colour attributes and resolves names to `svgs/v2/`
- [ ] T11: Document theming

### Checkpoint D: complete
- [ ] All success criteria in both specs are met
- [ ] Human review → merge

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Merging to `main` changes every live site at once | High | Legacy functions stay untouched except the rotation fix. Test each checkpoint on staging via the Netlify deploy preview, regression-check the legacy demo pages, and merge phase 1 on its own. |
| `document.currentScript` resolves wrong when Webflow loads the script differently (async, or cached) | Med | Fallback to the Netlify URL. Check on staging in T6. |
| `MutationObserver` cost on pages that change the DOM a lot (Webflow interactions) | Low | Only scan added nodes, use `querySelectorAll` on those subtrees, and skip anything already marked with `data-svg-state`. |
| CSS variable regex misreads an unusual Illustrator export | Med | Fixtures come from real files, and the T9 comparison page is checked by eye for every icon. |
| Injected `<style>` rules from v2 and legacy copies of the same icon on one page | Low | Class rules for the same name are identical in effect (v2 falls back to the same colours). Check this in T10. |
| Stripping the `<svg id>` breaks something that referenced it | Low | Nothing in the repo targets those IDs (all `Layer_N`). Rotation targets the placeholder, not the svg. |

## Decided (2026-11-10)

- Attributes use the short `data-svg` prefix (`data-svg`, `data-svg-duration`, `data-svg-accent`, ...), and the CSS variables match (`--svg-accent`, `--svg-base`).
- The faint strokes are called **base**.
- `v2/` leaves out the `-black`/`-white`/`-yellow` variants, because the colour attributes replace them.
- Netlify builds deploy previews only for pull requests against `main` (branch deploys are off). So T0 opens a **draft PR** from `feature/auto-loader-theming`, and every push updates `https://deploy-preview-<PR#>--vivus-svgs.netlify.app`. Checkpoints B and D are tested on staging against that URL before the PR is marked ready and merged.

## Open questions (none blocking)

- Per-element threshold, or is the global `0.5` enough? The default is global only.
