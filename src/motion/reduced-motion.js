/** @returns {boolean} */
export function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/**
 * @param {import("motion").AnimationOptions} opts
 * @returns {import("motion").AnimationOptions}
 */
export function motionOpts(opts = {}) {
  if (!prefersReducedMotion()) return opts;
  const { type: _type, stiffness: _s, damping: _d, repeat: _r, ...rest } = opts;
  return {
    ...rest,
    duration: Math.min(rest.duration ?? 0.2, 0.2),
    ease: "easeOut",
  };
}
