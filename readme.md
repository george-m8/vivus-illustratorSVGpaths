## Description
This project uses vivus.js to animate svgs that are exported from Adobe Illustrator as SVGs. The intended purpose is for SVGs using paths, not fills. I've implemented an observer which plays the animations when an SVG is seen on the page. If all SVGs are seen at the same time, further SVGs are animated following a small, compounding delay. So that this doesn't impact responsive layouts negatively, the script uses a global delay with timeout so that if multiple shapes are seen one-by-one as the page scrolls, there is no extra delay added.

## Intended Use
I've created this for use on a webflow site. By including the required code in a script tag, you can simply reference divs where the SVGs will be drawn.

## Example
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
## Issues
**Issue:** When using multiple svgs, styling conflicts
**Fix:** This is due to matching class names. Fix manually by renaming classes to be unique to the file. Or, run "process_svg.py" using the file name or directory as argument. The script will prepend all appearances of "cls" with a sanitised file name. This script features logic to skip already process files in a directory.
**Example:**
```bash
python3 process_svg.py ./svgs
```

**Issue:** SVG paths animate in the incorrect order.
**Fix:** SVGs animate in the order paths are present in the DOM. Either, edit the SVG contents so that your shapes/paths appear in correct order (first to appear is first animated), or rearrange the layers in Illustator (back layers animate before front layers).