# Rotation Feature - Quick Reference

## What's New

Added smart SVG rotation capability to the existing Vivus animation library. SVGs can now be rotated to specific angles via button/link clicks.

## Key Features

✅ **Shortest Path Rotation** - Always rotates via the most efficient route
   - Example: 270° to 10° rotates by -80° (not +300°)

✅ **Angle Normalization** - Handles any angle value
   - 720° → 0°
   - 450° → 90°
   - -90° → 270°

✅ **Smooth Transitions** - CSS-based with configurable duration

✅ **Independent Control** - Each SVG rotates independently

✅ **Flexible Selectors** - Works with buttons, links, any clickable element

## Quick Start

### 1. Initialize (same as before, plus rotation)

```javascript
document.addEventListener('DOMContentLoaded', function() {
  const shapes = [{
    containerId: 'myShape',
    svgUrl: 'svgs/play.svg',
    vivusOptions: { type: 'scenario-sync', duration: 36 },
    vivusInstance: null,
    isAnimated: false
  }];
  
  // Existing: Initialize animation
  initGlobalStaggerObserver(shapes, 0.5, false);
  
  // NEW: Initialize rotation
  initRotationControls(shapes, '[data-rotate-target]', 600, false);
});
```

### 2. Add HTML Controls

```html
<!-- SVG Container -->
<div id="myShape" class="svgContainer"></div>

<!-- Rotation Buttons -->
<button id="0deg" data-rotate-target="myShape">0°</button>
<button id="90deg" data-rotate-target="myShape">90°</button>
<button id="180deg" data-rotate-target="myShape">180°</button>
<button id="270deg" data-rotate-target="myShape">270°</button>

<!-- Also works with links -->
<a href="#" id="45deg" data-rotate-target="myShape">45°</a>
```

## How It Works

1. **Element ID** contains the target angle: `id="270deg"` or `id="270"`
2. **data-rotate-target** attribute points to the container ID
3. Click triggers rotation to that angle via shortest path

## API Reference

### initRotationControls()

```javascript
initRotationControls(shapeConfigs, controlSelector, duration, debug)
```

**Parameters:**
- `shapeConfigs` (Array) - Same shape configs from initGlobalStaggerObserver
- `controlSelector` (String) - CSS selector for controls [default: `'[data-rotate-target]'`]
- `duration` (Number) - Transition duration in ms [default: `600`]
- `debug` (Boolean) - Enable console logging [default: `false`]

**Returns:** API object with methods:
- `rotateSVG(containerId, angle)` - Rotate programmatically
- `getRotationState(containerId)` - Get current rotation state
- `normalizeAngle(angle)` - Normalize any angle to 0-360°

### Programmatic Usage

```javascript
const rotationAPI = initRotationControls(shapes);

// Rotate to 270°
rotationAPI.rotateSVG('myShape', 270);

// Get current angle
const state = rotationAPI.getRotationState('myShape');
console.log(state.currentAngle); // 270

// Normalize angle
rotationAPI.normalizeAngle(450); // Returns 90
```

## Examples

- **rotation-example.html** - Simple, minimal example
- **rotation-demo.html** - Comprehensive demo with all features
- **index.html** - Original example (still works as before)

## Files Modified

- **js/vivusObserver.js** - Added `initRotationControls()` function
- **readme.md** - Added rotation documentation

## Files Added

- **rotation-example.html** - Simple usage example
- **rotation-demo.html** - Full feature demo
- **ROTATION.md** - This file

## Compatibility

✅ Fully backward compatible - existing code works without changes
✅ Original animation features unchanged
✅ Optional feature - only initialize if needed

## Testing Edge Cases

```html
<!-- Angles over 360° -->
<button id="720deg" data-rotate-target="myShape">720° (= 0°)</button>
<button id="450deg" data-rotate-target="myShape">450° (= 90°)</button>

<!-- Negative angles -->
<button id="-90deg" data-rotate-target="myShape">-90° (= 270°)</button>

<!-- Without 'deg' suffix -->
<button id="180" data-rotate-target="myShape">180°</button>
```

All these work correctly with automatic normalization!

## Smart Rotation Examples

```
Current: 10°  → Target: 270° → Rotates: -100° (shortest path)
Current: 270° → Target: 10°  → Rotates: +100° (shortest path)
Current: 350° → Target: 10°  → Rotates: +20°  (via 360°/0°)
Current: 10°  → Target: 350° → Rotates: -20°  (via 0°)
```

The algorithm always chooses the path with the smallest absolute rotation!

## Auto-loaded icons

Rotation works on `data-svg` placeholders too (see [readme.md](readme.md#rotating-auto-loaded-icons)). Give the placeholder an `id` and pass `[{ containerId: '<id>' }]` to `initRotationControls`.

## Fix: long spins after wrapping past 0°

Older versions stored the normalised angle but applied the un-normalised one, so some sequences spun the long way round. For example, 0° → 350° → 10° turned a full 380°. The running applied angle is now tracked separately, so every click turns by at most 180°. `getRotationState().currentAngle` still reports 0-360°.
