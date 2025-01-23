/**
 * STAGGER_DELAY: time (ms) added each time a new shape is triggered
 * DECAY_TIMEOUT: if no shape triggers within this time, reset globalDelay to 0
 */
const STAGGER_DELAY = 800;
const DECAY_TIMEOUT = 800;

/**
 * initGlobalStaggerObserver
 * 
 * Observes multiple shapes (external SVGs fetched on demand). 
 * Whenever a shape becomes 50% visible (by default) and hasn't yet animated:
 *  - Schedules it after a globalDelay
 *  - Increments globalDelay by STAGGER_DELAY
 *  - Resets globalDelay to 0 if no new shape triggers within DECAY_TIMEOUT
 *
 * @param {Array} shapeConfigs - e.g. [
 *   {
 *     containerId: 'shape1',
 *     svgUrl: 'svgs/play.svg',
 *     vivusOptions: { type: 'scenario-sync', duration: 150 },
 *     vivusInstance: null,
 *     isAnimated: false
 *   }, ...
 * ]
 * @param {number} [threshold=0.5] - Intersection threshold (0..1)
 * @param {boolean} [debug=false]  - If true, logs debug info
 */
function initGlobalStaggerObserver(shapeConfigs, threshold = 0.5, debug = false) {
  // A single IntersectionObserver
  const observer = new IntersectionObserver(onIntersect, { threshold });

  // The "global" delay accumulator and its decay timer
  let globalDelay = 0;
  let decayTimer = null;

  /**
   * onIntersect
   * Called whenever any observed element crosses the threshold
   */
  function onIntersect(entries) {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return; // We only care about entering the viewport

      // Find the shape config for this container
      const config = shapeConfigs.find(cfg => {
        const container = document.getElementById(cfg.containerId);
        return container === entry.target;
      });
      if (!config) return;

      // If it's already animated, skip
      if (config.isAnimated) return;

      // We have a new shape entering view that needs animating
      scheduleShapeAnimation(config);
    });
  }

  /**
   * scheduleShapeAnimation
   * Schedules a shape's Vivus animation using the current globalDelay.
   * Then increments globalDelay by STAGGER_DELAY.
   * Resets the globalDelay to 0 after DECAY_TIMEOUT if no new shape appears.
   */
  function scheduleShapeAnimation(config) {
    if (debug) {
      console.log(`[scheduleShapeAnimation] Triggering ${config.containerId}; current globalDelay=${globalDelay}ms`);
    }

    // Animate this shape after globalDelay
    setTimeout(() => {
      if (debug) {
        console.log(`[scheduleShapeAnimation] Animating ${config.containerId} now`);
      }
      config.vivusInstance.play();
      config.isAnimated = true;
    }, globalDelay);

    // Increment globalDelay for the *next* shape
    globalDelay += STAGGER_DELAY;

    // Reset decay timer
    if (decayTimer) clearTimeout(decayTimer);
    decayTimer = setTimeout(() => {
      // If no new shapes triggered in the last DECAY_TIMEOUT ms, reset
      globalDelay = 0;
      if (debug) {
        console.log(`[scheduleShapeAnimation] globalDelay reset to 0 (decay).`);
      }
    }, DECAY_TIMEOUT);
  }

  // 1. Fetch each SVG, inject, create Vivus, then observe its container
  shapeConfigs.forEach(cfg => {
    const container = document.getElementById(cfg.containerId);
    if (!container) {
      if (debug) console.error(`[initGlobalStaggerObserver] Container not found: ${cfg.containerId}`);
      return;
    }

    // Fetch the SVG
    if (debug) {
      console.log(`[initGlobalStaggerObserver] Fetching SVG for ${cfg.containerId}: ${cfg.svgUrl}`);
    }

    fetch(cfg.svgUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Failed to fetch ${cfg.svgUrl}: ${response.status} ${response.statusText}`);
        }
        return response.text();
      })
      .then(svgText => {
        // Inject raw SVG
        container.innerHTML = svgText;
        const svgElem = container.querySelector('svg');
        if (!svgElem) throw new Error(`No <svg> found in ${cfg.svgUrl}`);

        // Convert shapes to <path> for Vivus
        new Pathformer(svgElem);

        // Create Vivus instance (manual start)
        cfg.vivusInstance = new Vivus(svgElem, {
          ...cfg.vivusOptions,
          start: 'manual'
        });

        // Observe container AFTER injection
        observer.observe(container);
        if (debug) {
          console.log(`[initGlobalStaggerObserver] Observing ${cfg.containerId} after injection`);
        }
      })
      .catch(err => console.error('[initGlobalStaggerObserver] Error:', err));
  });
}