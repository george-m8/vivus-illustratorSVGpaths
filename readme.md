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
          vivusOptions: { type: 'scenario-sync', duration: 120, animTimingFunction: Vivus.EASE },
          vivusInstance: null,
          isAnimated: false,
          isIntersecting: false
        },
        {
          containerId: 'eventsShapeContainer',
          svgUrl: 'svgs/events.svg',
          vivusOptions: { type: 'scenario-sync', duration: 120, animTimingFunction: Vivus.EASE },
          vivusInstance: null,
          isAnimated: false,
          isIntersecting: false
        },
        {
          containerId: 'consultShapeContainer',
          svgUrl: 'svgs/consult.svg',
          vivusOptions: { type: 'scenario-sync', duration: 120, animTimingFunction: Vivus.EASE },
          vivusInstance: null,
          isAnimated: false,
          isIntersecting: false
        }
      ];

      initShapeObserver(shapes, 0.5); // 50% visible threshold
    });
  </script>