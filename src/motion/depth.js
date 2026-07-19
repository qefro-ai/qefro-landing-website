import { prefersReducedMotion } from "./reduced-motion.js";

/**
 * Cursor-tracking 3D tilt was removed to keep the site smooth and fast.
 * Cards now use a lightweight CSS hover lift (see styles.css). This keeps
 * the module present for the boot chain without running any rAF loops.
 */
export function initDepth() {
  // Intentionally empty — no per-frame work.
}
