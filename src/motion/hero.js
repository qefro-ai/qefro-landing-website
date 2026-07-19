import { animate } from "motion";
import { motionOpts, prefersReducedMotion } from "./reduced-motion.js";

export function initHero() {
  const hero = document.querySelector(".hero");
  if (!hero) return;

  const reduced = prefersReducedMotion();
  const parts = [
    hero.querySelector("[data-motion='hero-badge']"),
    hero.querySelector("[data-motion='hero-title']"),
    hero.querySelector("[data-motion='hero-sub']"),
    hero.querySelector("[data-motion='hero-actions']"),
    hero.querySelector("[data-motion='hero-checks']"),
    hero.querySelector("[data-motion='hero-diff']"),
    hero.querySelector("[data-motion='hero-cue']"),
  ].filter(Boolean);

  parts.forEach((el) => {
    el.style.opacity = reduced ? "1" : "0";
    if (!reduced) el.style.transform = "translateY(16px)";
  });

  const run = () => {
    parts.forEach((el, i) => {
      animate(
        el,
        { opacity: 1, y: 0 },
        motionOpts({ duration: 0.35, delay: reduced ? 0 : i * 0.07, ease: "easeOut" })
      );
    });
  };

  if (reduced) {
    run();
  } else {
    // Hero is above the fold — single, cheap intro pass (no infinite loops)
    requestAnimationFrame(run);
  }
}
