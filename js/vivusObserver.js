/**
 * Delay (in ms) between each shape's start in the staggered sequence
 */
const STAGGER_DELAY = 800;

/**
 * Initialize IntersectionObserver-based animations for multiple shapes.
 *
 * @param {Array} shapeConfigs
 * @param {number} [threshold=0.5]
 * @param {boolean} [debug=false] 
 */
function initShapeObserver(shapeConfigs, threshold = 0.5, debug = false) {
  if (debug) console.log('[initShapeObserver] Starting setup...');

  const observer = new IntersectionObserver((entries, obs) => {
    if (debug) console.log('[IntersectionObserver] Callback triggered.');

    entries.forEach(entry => {
      const config = shapeConfigs.find(cfg => {
        const c = document.getElementById(cfg.containerId);
        return c === entry.target;
      });
      if (!config) return;

      config.isIntersecting = entry.isIntersecting;
      if (debug) {
        console.log(
          `[IntersectionObserver] ${config.containerId} isIntersecting:`,
          config.isIntersecting
        );
      }
    });

    // Check if all are in view & none animated
    const allInView = shapeConfigs.every(cfg => cfg.isIntersecting);
    const noneAnimated = !shapeConfigs.some(cfg => cfg.isAnimated);

    if (allInView && noneAnimated) {
      // Staggered animation across all shapes
      if (debug) console.log('[IntersectionObserver] All in view => Staggered animation.');
      doStaggeredAnimation(shapeConfigs, obs, debug);
    } else {
      // Otherwise animate individually
      shapeConfigs.forEach(cfg => {
        if (cfg.isIntersecting && !cfg.isAnimated && cfg.vivusInstance) {
          if (debug) {
            console.log(`[IntersectionObserver] Attempt animate: ${cfg.containerId}`);
          }
          triggerShapeAnimation(cfg, 0, debug);
        }
      });
    }
  }, { threshold });

  // For each shape, fetch & inject the SVG, create Vivus, then observe
  shapeConfigs.forEach(cfg => {
    const container = document.getElementById(cfg.containerId);
    if (!container) {
      console.error('[initShapeObserver] Container not found:', cfg.containerId);
      return;
    }

    if (debug) {
      console.log(`[initShapeObserver] Fetching SVG for ${cfg.containerId}: ${cfg.svgUrl}`);
    }

    fetch(cfg.svgUrl)
      .then(resp => {
        if (!resp.ok) {
          throw new Error(`Failed to fetch SVG: ${resp.status} ${resp.statusText}`);
        }
        return resp.text();
      })
      .then(svgText => {
        container.innerHTML = svgText;
        const svgElem = container.querySelector('svg');
        if (!svgElem) throw new Error('[initShapeObserver] No <svg> found in fetched content.');

        // Convert shapes
        new Pathformer(svgElem);

        // Create Vivus instance
        cfg.vivusInstance = new Vivus(svgElem, {
          ...cfg.vivusOptions,
          start: 'manual'
        });
        if (debug) {
          console.log(`[initShapeObserver] Created Vivus instance for ${cfg.containerId}`);
        }

        // *** Now that the container has content, let's observe it ***
        observer.observe(container);
        if (debug) {
          console.log(`[initShapeObserver] Observing ${cfg.containerId} AFTER injection`);
        }
      })
      .catch(err => console.error('[initShapeObserver] Error loading SVG:', err));
  });
}

/**
 * Stagger all shapes in the array (the order is the array order).
 * Once triggered, unobserve them so they aren't re-triggered.
 */
function doStaggeredAnimation(shapeConfigs, observer, debug) {
  let delayAccumulator = 0;
  shapeConfigs.forEach(cfg => {
    if (!cfg.vivusInstance) return;
    if (debug) {
      console.log(`[doStaggeredAnimation] Scheduling ${cfg.containerId} at +${delayAccumulator}ms.`);
    }
    triggerShapeAnimation(cfg, delayAccumulator, debug);
    delayAccumulator += STAGGER_DELAY;
  });

  // Unobserve all
  shapeConfigs.forEach(cfg => {
    const c = document.getElementById(cfg.containerId);
    if (c) observer.unobserve(c);
  });
}

/**
 * Actually start the shape's animation after the specified delay.
 */
function triggerShapeAnimation(cfg, delayMs, debug) {
  if (cfg.isAnimated) return; // Already played

  if (delayMs === 0) {
    // Animate right away
    if (debug) {
      console.log(`[triggerShapeAnimation] ${cfg.containerId} animates immediately`);
    }
    cfg.vivusInstance.play();
    cfg.isAnimated = true;
  } else {
    // Animate after a delay
    if (debug) {
      console.log(`[triggerShapeAnimation] ${cfg.containerId} waiting ${delayMs}ms`);
    }
    setTimeout(() => {
      cfg.vivusInstance.play();
      cfg.isAnimated = true;
      if (debug) {
        console.log(`[triggerShapeAnimation] Now animating ${cfg.containerId}`);
      }
    }, delayMs);
  }
}