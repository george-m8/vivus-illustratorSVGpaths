/**
 * STAGGER_DELAY: time (ms) added each time a new shape is triggered
 * DECAY_TIMEOUT: if no shape triggers within this time, reset globalDelay to 0
 */
const STAGGER_DELAY = 800;
const DECAY_TIMEOUT = 800;

/**
 * DEFAULT_ROTATION_DURATION: default duration (ms) for rotation transitions
 */
const DEFAULT_ROTATION_DURATION = 600;

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

/**
 * initRotationControls
 * 
 * Enables rotation of SVGs via button/link clicks. The target angle is derived
 * from the clicked element's ID (e.g., id="270deg" → rotate to 270°).
 * 
 * Features:
 * - Normalizes angles to 0-360° range
 * - Rotates via shortest path (e.g., 270° to 10° goes via 0°, not backwards through 180°)
 * - Smooth CSS transitions
 * 
 * @param {Array} shapeConfigs - Same shape configs from initGlobalStaggerObserver
 * @param {string} [controlSelector='[data-rotate-target]'] - CSS selector for rotation controls
 * @param {number} [duration=DEFAULT_ROTATION_DURATION] - Rotation transition duration (ms)
 * @param {boolean} [debug=false] - Enable debug logging
 * 
 * Usage:
 * HTML: <button id="90deg" data-rotate-target="playShapeContainer">Rotate to 90°</button>
 * JS: initRotationControls(shapes, '[data-rotate-target]', 600, true);
 */
function initRotationControls(shapeConfigs, controlSelector = '[data-rotate-target]', duration = DEFAULT_ROTATION_DURATION, debug = false) {
  // Track current rotation angle for each container
  const rotationState = {};
  
  // Initialize rotation state for each shape
  shapeConfigs.forEach(cfg => {
    rotationState[cfg.containerId] = {
      currentAngle: 0,   // normalised 0-360, reported via getRotationState
      targetAngle: 0,
      appliedAngle: 0    // running CSS rotate() value, may go beyond 0-360
    };
  });
  
  /**
   * Normalize angle to 0-360 range
   */
  function normalizeAngle(angle) {
    angle = angle % 360;
    if (angle < 0) angle += 360;
    return angle;
  }
  
  /**
   * Calculate shortest rotation path between two angles
   * Returns the delta that should be applied
   */
  function calculateShortestPath(from, to) {
    from = normalizeAngle(from);
    to = normalizeAngle(to);
    
    let delta = to - from;
    
    // If going the "long way" around, take the short path instead
    if (delta > 180) {
      delta -= 360;
    } else if (delta < -180) {
      delta += 360;
    }
    
    return delta;
  }
  
  /**
   * Rotate an SVG to a specific angle
   */
  function rotateSVG(containerId, targetAngle, transitionDuration = duration) {
    const container = document.getElementById(containerId);
    if (!container) {
      if (debug) console.error(`[initRotationControls] Container not found: ${containerId}`);
      return;
    }
    
    const svg = container.querySelector('svg');
    if (!svg) {
      if (debug) console.error(`[initRotationControls] No SVG found in: ${containerId}`);
      return;
    }
    
    const state = rotationState[containerId];
    if (!state) {
      if (debug) console.error(`[initRotationControls] No rotation state for: ${containerId}`);
      return;
    }
    
    // Normalize target angle
    targetAngle = normalizeAngle(targetAngle);
    
    // Calculate shortest path
    const delta = calculateShortestPath(state.currentAngle, targetAngle);
    // Build on the angle actually applied, so the CSS transition always
    // moves by `delta` (applying currentAngle + delta could spin the long way)
    const newAngle = state.appliedAngle + delta;
    
    if (debug) {
      console.log(`[initRotationControls] Rotating ${containerId}:`, {
        from: state.currentAngle,
        to: targetAngle,
        delta: delta,
        newAngle: newAngle
      });
    }
    
    // Apply transition
    svg.style.transition = `transform ${transitionDuration}ms ease-in-out`;
    svg.style.transformOrigin = 'center center';
    svg.style.transform = `rotate(${newAngle}deg)`;
    
    // Update state - appliedAngle keeps the running value (may exceed 360),
    // currentAngle/targetAngle stay normalised for path calculations
    state.appliedAngle = newAngle;
    state.currentAngle = targetAngle;
    state.targetAngle = targetAngle;
  }
  
  /**
   * Parse angle from element ID
   * Supports formats: "90deg", "180", "270deg", etc.
   */
  function parseAngleFromId(id) {
    if (!id) return null;
    
    // Remove "deg" suffix if present and parse number
    const match = id.match(/^(-?\d+(?:\.\d+)?)(deg)?$/);
    if (match) {
      return parseFloat(match[1]);
    }
    
    return null;
  }
  
  // Set up event listeners for rotation controls
  document.addEventListener('click', function(event) {
    const control = event.target.closest(controlSelector);
    if (!control) return;
    
    event.preventDefault();
    
    const targetContainerId = control.dataset.rotateTarget || control.getAttribute('data-rotate-target');
    const angle = parseAngleFromId(control.id);
    
    if (!targetContainerId) {
      if (debug) console.warn('[initRotationControls] No data-rotate-target specified on control:', control);
      return;
    }
    
    if (angle === null) {
      if (debug) console.warn('[initRotationControls] Could not parse angle from ID:', control.id);
      return;
    }
    
    rotateSVG(targetContainerId, angle);
  });
  
  if (debug) {
    console.log('[initRotationControls] Initialized with selector:', controlSelector);
  }
  
  // Return API for programmatic rotation
  return {
    rotateSVG: rotateSVG,
    getRotationState: (containerId) => rotationState[containerId],
    normalizeAngle: normalizeAngle
  };
}