/** @returns {boolean} */
export function prefersReducedMotion() {
  return true;
}

/**
 * @param {import("motion").AnimationOptions} opts
 * @returns {import("motion").AnimationOptions}
 */
export function motionOpts(opts = {}) {
  return opts;
}
