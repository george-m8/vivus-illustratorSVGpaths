## Head code (site-wide, once)
```html
  <script src="https://cdn.jsdelivr.net/npm/vivus@0.4.4/dist/vivus.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/vivus@0.4.4/src/pathformer.js"></script>
  
  <script src="https://vivus-svgs.netlify.app/js/vivusObserver.js"></script>
```

## Placeholder (anywhere, any page)
```html
<div data-svg="play"></div>
```

Optional attributes: `data-svg-duration="36"`, `data-svg-type="scenario-sync"`. The same icon can be used any number of times on a page. No body script or IDs needed. See [readme.md](readme.md#quick-start-recommended) for details.

---

## Legacy method (still supported)

### SVG container example (Place above body script)
```html
<div id="playShapeContainer"></div> <!-- ID is must match script below -->
```

### Body script (Place below SVG containers)
```html
<script>
    document.addEventListener('DOMContentLoaded', function() {
      const shapes = [
        {
          containerId: 'playShapeContainer',
          svgUrl: 'https://vivus-svgs.netlify.app/svgs/play.svg',
          vivusOptions: { type: 'scenario-sync', duration: 36 },
          vivusInstance: null,
          isAnimated: false
        }
        // Add more shapes/svgs to this constant
      ];
      
      // Initialize the observer with threshold=0.5, debug=true
      initGlobalStaggerObserver(shapes, 0.5, true);
    });
</script>
```
