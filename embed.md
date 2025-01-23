## Head code
```html
  <script src="https://cdn.jsdelivr.net/npm/vivus@0.4.4/dist/vivus.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/vivus@0.4.4/src/pathformer.js"></script>
  
  <script src="https://vivus-svgs.netlify.app/js/vivusObserver.js"></script>
```

## SVG container example (Place above body script)
```html
<div id="playShapeContainer"></div> <!-- ID is must match script below -->
```

## Body script (Place below SVG containers)
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