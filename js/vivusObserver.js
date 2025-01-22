/**
 * Global stagger delay between shapes (in milliseconds).
 * Adjust as desired.
 */
const STAGGER_DELAY = 800;

/**
 * Global delay remaining. If > 0, new shapes must wait that many ms.
 */
let globalDelay = 0;

/**
 * So we can cancel/replace the timeout that resets `globalDelay`.
 */
let globalTimeoutId = null;

/**
 * Initialize shape observer for multiple shapes, each with:
 *   {
 *     containerId: string,
 *     svgUrl: string,
 *     vivusOptions: object,
 *     vivusInstance: null,   // set after fetching
 *     isAnimated: false,     // becomes true once played
 *     isIntersecting: false  // updated by IntersectionObserver
 *   }
 * 
 * @param {Array} shapeConfigs 
 * @param {number} [threshold=0.5] Intersection threshold (0 to 1)
 * @param {boolean} [debug=false] If true, logs debug info to console
 */
function initShapeObserver(shapeConfigs, threshold = 0.5, debug = true) {
  if (debug) console.log('[initShapeObserver] Starting setup...');

  // 1) Fetch each SVG, create Vivus instance (start: manual)
  shapeConfigs.forEach(cfg => {
    const container = document.getElementById(cfg.containerId);
    if (!container) {
      console.error('[initShapeObserver] Container not found:', cfg.containerId);
      return;
    }
    fetch(cfg.svgUrl)
      .then(resp => {
        if (!resp.ok) {
          throw new Error(`Failed to fetch SVG: ${resp.status} ${resp.statusText}`);
        }
        return resp.text();
      })
      .then(svgText => {
        // Inject the SVG
        container.innerHTML = svgText;
        const svgElem = container.querySelector('svg');
        if (!svgElem) throw new Error('No <svg> in fetched content.');

        // Convert shapes to <path> for Vivus
        new Pathformer(svgElem);

        // Create Vivus instance, but don't auto-play
        cfg.vivusInstance = new Vivus(svgElem, {
          ...cfg.vivusOptions,
          start: 'manual'
        });
        if (debug) {
          console.log(`[initShapeObserver] Created Vivus instance for ${cfg.containerId}`);
        }
      })
      .catch(err => console.error('[initShapeObserver] Error loading SVG:', err));
  });

  // 2) IntersectionObserver: watch all containers
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      const cfg = shapeConfigs.find(sc => {
        const el = document.getElementById(sc.containerId);
        return el === entry.target;
      });
      if (cfg) {
        cfg.isIntersecting = entry.isIntersecting;

        // If visible AND not animated, try to animate
        if (cfg.isIntersecting && !cfg.isAnimated && cfg.vivusInstance) {
          if (debug) console.log(`[IntersectionObserver] Attempt animate: ${cfg.containerId}`);
          triggerShapeAnimation(cfg, debug);
        }
      }
    });
  }, { threshold });

  // 3) Attach observer to each container
  shapeConfigs.forEach(cfg => {
    const container = document.getElementById(cfg.containerId);
    if (container) observer.observe(container);
    if (debug) console.log('[initShapeObserver] Observing', cfg.containerId);
  });
}

/**
 * Handles the logic for playing a shape's animation, taking into account
 * the global delay. If globalDelay > 0, it waits that many ms before playing
 * (and extends the global delay). If globalDelay=0, it plays immediately.
 * 
 * @param {Object} cfg - shape config (must have vivusInstance)
 * @param {boolean} debug 
 */
function triggerShapeAnimation(cfg, debug) {
  if (!cfg.vivusInstance) return;

  if (globalDelay > 0) {
    // Delay is still active => schedule shape after that remainder
    if (debug) {
      console.log(`[triggerShapeAnimation] ${cfg.containerId} waiting ${globalDelay}ms`);
    }
    setTimeout(() => {
      cfg.vivusInstance.play();
      cfg.isAnimated = true;
      if (debug) console.log(`[triggerShapeAnimation] Now animating ${cfg.containerId}`);
    }, globalDelay);

    // Extend the global delay by STAGGER_DELAY
    globalDelay += STAGGER_DELAY;

  } else {
    // No delay => animate now
    if (debug) {
      console.log(`[triggerShapeAnimation] ${cfg.containerId} animates immediately`);
    }
    cfg.vivusInstance.play();
    cfg.isAnimated = true;

    // Set global delay for the next shape
    globalDelay = STAGGER_DELAY;
  }

  // Reset the existing timer (if any) so we can push it out
  if (globalTimeoutId) {
    clearTimeout(globalTimeoutId);
    globalTimeoutId = null;
  }

  // Create new timer to set the delay back to 0 after the new globalDelay
  globalTimeoutId = setTimeout(() => {
    if (debug) console.log('[triggerShapeAnimation] globalDelay reset to 0');
    globalDelay = 0;
    globalTimeoutId = null;
  }, globalDelay);
}