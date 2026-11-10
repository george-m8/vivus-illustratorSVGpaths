## Description
This project uses vivus.js to animate svgs that are exported from Adobe Illustrator as SVGs. The intended purpose is for SVGs using paths, not fills. I've implemented an observer which plays the animations when an SVG is seen on the page. If all SVGs are seen at the same time, further SVGs are animated following a small, compounding delay. So that this doesn't impact responsive layouts negatively, the script uses a global delay with timeout so that if multiple shapes are seen one-by-one as the page scrolls, there is no extra delay added.

## Intended Use
I've created this for use on a webflow site. Add three script tags to the site-wide head code once, then drop placeholder divs wherever an icon should appear. No per-page script is needed.

## Quick start (recommended)

Head code, added once for the whole site:
```html
<script src="https://cdn.jsdelivr.net/npm/vivus@0.4.4/dist/vivus.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vivus@0.4.4/src/pathformer.js"></script>
<script src="https://vivus-svgs.netlify.app/js/vivusObserver.js"></script>
```

Placeholder, anywhere on any page (inside components too, as many times as you like):
```html
<div data-svg="play"></div>
```

| Attribute | Default | Meaning |
|---|---|---|
| `data-svg` | (required) | An SVG name (`play` loads the colourable `svgs/v2/play.svg` from wherever `vivusObserver.js` is served), or a full URL/path (anything containing `/` or ending `.svg`), e.g. `svgs/play.svg` for the original |
| `data-svg-duration` | `36` | Vivus `duration` |
| `data-svg-type` | `scenario-sync` | Vivus `type` |
| `data-svg-accent` | the icon's own colour | Accent stroke colour, any CSS colour |
| `data-svg-base` | white | Faint strokes: `light` (white), `dark` (black) or any CSS colour |
| `data-svg-accent-1`, `-2`, `-3` | the icon's own colours | Individual colours of multi-colour icons (`dh-logo`: red, yellow, blue) |
| `data-svg-state` | (set by the script) | `loading`, `ready`, `animated` or `error`. Useful for styling and debugging. |

- Each copy of an icon animates on its own as it scrolls into view, and each SVG file is downloaded only once per page.
- Placeholders added after the page loads (tabs, sliders, CMS "load more") are picked up automatically.
- A bad name sets `data-svg-state="error"` and logs one console error. Other icons still load.
- For debug logging, set `window.VIVUS_DEBUG = true` before the script tag.

## Colours

Icons loaded by name come from `svgs/v2/`. These are copies of the originals whose strokes use CSS variables, and each variable falls back to the original colour. With nothing set they look exactly like the originals.

```html
<div data-svg="play" data-svg-accent="#ff6b6b"></div>                 <!-- coloured accent -->
<div data-svg="play" data-svg-base="dark"></div>                      <!-- faint lines black, for light backgrounds -->
<div data-svg="dh-logo" data-svg-accent="#fcee21"></div>              <!-- multi-colour icon in one colour -->
<div data-svg="dh-logo" data-svg-accent-2="#ff6b6b"></div>            <!-- change just the yellow -->
```

Or set the variables in CSS on any parent (Webflow custom properties work too):

```css
.hero { --svg-accent: #ff6b6b; --svg-base: #000; }
```

| Variable | Applies to |
|---|---|
| `--svg-accent` | Accent strokes |
| `--svg-accent-1`, `-2`, `-3` | Each colour of a multi-colour icon (falls back to `--svg-accent`) |
| `--svg-base` | Faint strokes (always at 40% opacity) |

The colour copies of icons aren't in `v2/`, because attributes replace them:

| Original file | v2 equivalent |
|---|---|
| `X-black.svg` (book, business, contact, event, interviewer, mail, services) | `data-svg="X" data-svg-accent="#000"` |
| `dh-logo-black.svg` | `data-svg="dh-logo" data-svg-accent="#000"` |
| `dh-logo-white.svg` | `data-svg="dh-logo" data-svg-accent="#fff"` |
| `dh-logo-yellow.svg` | `data-svg="dh-logo" data-svg-accent="#fcee21"` |
| `interviewer-white.svg` | `data-svg="interviewer" data-svg-accent="#fff"` |

### Adding a new icon

1. Export from Illustrator into `svgs/` and run `process_svg.py` on it (unique class names).
2. Generate its colourable copy:
   ```bash
   uv run python theme_svg.py ./svgs ./svgs/v2
   ```
   This rewrites `svgs/v2/` from the originals and never modifies `svgs/`. Rules that set `opacity` become base strokes, and other strokes become accents. Files ending `-black`, `-white` or `-yellow` are skipped.
3. Add the name to `NAMES` in `test-themed.html`, open it, and check it reads `ALL PASS`.
4. Run the tests:
   ```bash
   uv run pytest
   ```

## Legacy method (per-page script)

The original ID-based method still works unchanged, and existing sites need no changes. New pages should use the quick start above.

```html
  <!-- Vivus & Pathformer (CDN or local) -->
  <script src="https://cdn.jsdelivr.net/npm/vivus@0.4.4/dist/vivus.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/vivus@0.4.4/src/pathformer.js"></script>
  
  <!-- Our custom code with the refined logic -->
  <script src="js/vivusObserver.js"></script>

  <div class="svgRow">
    <div id="playShapeContainer" class="svgContainer"></div>
    <div id="eventsShapeContainer" class="svgContainer"></div>
    <div id="consultShapeContainer" class="svgContainer"></div>
  </div>
  
  <script>
    document.addEventListener('DOMContentLoaded', function() {
      const shapes = [
        {
          containerId: 'playShapeContainer',
          svgUrl: 'svgs/play.svg',
          vivusOptions: { type: 'scenario-sync', duration: 36 },
          vivusInstance: null,
          isAnimated: false
        },
        {
          containerId: 'eventsShapeContainer',
          svgUrl: 'svgs/events.svg',
          vivusOptions: { type: 'scenario-sync', duration: 36 },
          vivusInstance: null,
          isAnimated: false
        },
        {
          containerId: 'consultShapeContainer',
          svgUrl: 'svgs/consult.svg',
          vivusOptions: { type: 'scenario-sync', duration: 36 },
          vivusInstance: null,
          isAnimated: false
        }
      ];
      
      // Initialize the observer with threshold=0.5, debug=true
      initGlobalStaggerObserver(shapes, 0.5, true);
    });
  </script>
```
## Rotation Feature

The library now supports rotating SVGs to specific angles via button/link clicks. The rotation feature:
- **Shortest path rotation**: Automatically rotates via the most efficient route (e.g., 270° to 10° rotates by -80°, not +300°)
- **Angle normalization**: Handles angles over 360° (720° becomes 0°, 450° becomes 90°)
- **Smooth transitions**: CSS-based smooth rotation with configurable duration
- **Independent control**: Each SVG can be rotated independently
- **Works with any clickable element**: Buttons, links, etc.

### Usage

```html
<script>
  document.addEventListener('DOMContentLoaded', function() {
    const shapes = [
      {
        containerId: 'playShapeContainer',
        svgUrl: 'svgs/play.svg',
        vivusOptions: { type: 'scenario-sync', duration: 36 },
        vivusInstance: null,
        isAnimated: false
      }
    ];
    
    // Initialize drawing/animation
    initGlobalStaggerObserver(shapes, 0.5, false);
    
    // Initialize rotation controls
    // Selector: elements with [data-rotate-target] attribute
    // Duration: 600ms transition
    // Debug: true/false
    initRotationControls(shapes, '[data-rotate-target]', 600, false);
  });
</script>

<!-- Rotation controls -->
<button id="0deg" data-rotate-target="playShapeContainer">0°</button>
<button id="90deg" data-rotate-target="playShapeContainer">90°</button>
<button id="180deg" data-rotate-target="playShapeContainer">180°</button>
<button id="270deg" data-rotate-target="playShapeContainer">270°</button>

<!-- Also works with links -->
<a href="#" id="45deg" data-rotate-target="playShapeContainer">45°</a>
```

### How It Works

1. **Element ID contains the angle**: `id="270deg"` or `id="270"` both work
2. **data-rotate-target attribute**: Points to the container ID to rotate
3. **Angle parsing**: Supports formats like "90deg", "180", "-90deg"
4. **Smart rotation**: Always takes shortest path between angles

### Programmatic API

```javascript
// Returns API object
const rotationAPI = initRotationControls(shapes);

// Rotate programmatically
rotationAPI.rotateSVG('playShapeContainer', 270);

// Get current rotation state
const state = rotationAPI.getRotationState('playShapeContainer');
console.log(state.currentAngle); // e.g., 270

// Normalize any angle
const normalized = rotationAPI.normalizeAngle(450); // Returns 90
```

### Demo

See [rotation-demo.html](rotation-demo.html) for a complete working example with multiple scenarios.

### Rotating auto-loaded icons

Rotation also works on quick-start placeholders. Give the placeholder an `id` and pass it to `initRotationControls`:

```html
<div id="pillars" data-svg="dh-logo-yellow"></div>
<button id="90deg" data-rotate-target="pillars">90°</button>
<script>
  document.addEventListener('DOMContentLoaded', () => initRotationControls([{ containerId: 'pillars' }]));
</script>
```

## Local testing

```bash
uv run --no-project python dev_server.py
```

Then open `http://localhost:8000/test-auto.html`. `test-themed.html` compares every original icon with its v2 copy pixel by pixel, and `uv run pytest` tests `theme_svg.py`. It's a self-checking page whose summary line reads `ALL PASS` or `N FAILED`. Keep the tab visible, because hidden tabs don't fire the scroll-into-view checks. `dev_server.py` disables caching so edits show up on reload.

## Issues
**Issue:** When using multiple svgs, styling conflicts
**Fix:** This is due to matching class names. Fix manually by renaming classes to be unique to the file. Or, run "process_svg.py" using the file name or directory as argument. The script will prepend all appearances of "cls" with a sanitised file name. This script features logic to skip already process files in a directory.
**Example:**
```bash
uv run --no-project python process_svg.py ./svgs
```

**Issue:** SVG paths animate in the incorrect order.
**Fix:** SVGs animate in the order paths are present in the DOM. Either, edit the SVG contents so that your shapes/paths appear in correct order (first to appear is first animated), or rearrange the layers in Illustator (back layers animate before front layers).